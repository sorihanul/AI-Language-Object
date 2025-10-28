/*
  AILO–SCP v0.9-E Studio (Single-file TSX)
  -------------------------------------------------
  Purpose: A self-contained web UI to author, lint, format, and serialize
           AILO statements, with CJON round-trip, slot canonicalization,
           basic validation (E-codes), and hash/sign placeholders.

  Tech: React + Tailwind + shadcn/ui (Button, Card, Input, Textarea),
        lucide-react for icons. No external runtime services required.

  Notes:
  - This is a single-file component intended for quick drop-in to a
    Vite/Next.js/CRA project with Tailwind & shadcn installed.
  - Crypto hashing uses Web Crypto (SHA-256). Signature is mocked.
  - Parser targets AILO surface subset faithful to v0.9-E:
      VERB { slot: value, ... } MOOD(?) | MOOD(!) | MOOD(.)
    Values: numbers, strings, idents, quantity (e.g., 2cm, 90C, 60%),
            arrays, maps (ident{...}), tuples (...), sets |...|,
            choices //a//b//, durations 2h30m, ISO-8601 times.
    This is a pragmatic parser (sufficient for most examples),
    not a complete EBNF-level implementation.

  MIT License © 2025 sorihanul
*/

import * as React from "react";
import { useEffect, useMemo, useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Copy, Download, Hash, Sparkles, Play, RotateCcw, Check, X, Upload, FileText, ArrowRight } from "lucide-react";

// ---------- AILO Core Types ----------

type Mood = "?" | "!" | ".";

const CANONICAL_ORDER = [
  "ag","obj","to","state","why","rule","gain","risk","if","when","where","with","limit","cost","conf","src","ref","note","id"
] as const;

const KNOWN_VERBS = new Set([
  // Core 12
  "see","want","set","decide","check","learn","map","link","judge","act","recover","end",
  // Extended (common)
  "plan","fetch","filter","sort","group","sample","infer","explain","verify","log","notify","reserve","move","grasp","cut","heat","cool","mix","assemble","deploy","rollback"
]);

// ---------- Utilities ----------

function clamp01(x:number){return Math.max(0,Math.min(1,x));}

function sha256Hex(buf: Uint8Array): Promise<string> {
  return crypto.subtle.digest("SHA-256", buf).then(d => {
    const a = new Uint8Array(d); let s = ""; for (const b of a) s += b.toString(16).padStart(2,"0");
    return s;
  });
}

function enc(s:string){return new TextEncoder().encode(s)}

function isQuantityToken(tok:string){
  // e.g., 2cm, 120C, 60% (-> percent), 24h, 1.5s, 3kg
  return /^[-+]?\d+(?:\.\d+)?(?:e[-+]?\d+)?[A-Za-z%°]+$/.test(tok);
}

function parseNumber(tok:string){
  const n = Number(tok);
  return Number.isFinite(n) ? n : null;
}

function tryJsonParse(s:string){
  try{return JSON.parse(s)}catch{return null}
}

// Simple tokenizer respecting braces/quotes/choices
function splitTopLevelSlots(s:string): string[] {
  const out:string[]=[]; let cur=""; let depth=0; let inStr=false; let choice=0;
  for (let i=0;i<s.length;i++){
    const c=s[i], n=s[i+1];
    if(!inStr && c==="/" && n==="/") { choice^=1; i++; cur+="//"; continue; }
    if(!choice){
      if(c==='"'){ inStr=!inStr; cur+=c; continue; }
      if(!inStr){
        if(c==='{'||c==='['||c==='('|c==='|') depth++
        if(c==='}'||c===']'||c===')'||c==='|') depth=Math.max(0,depth-1)
        if(c===',' && depth===0){ out.push(cur.trim()); cur=""; continue; }
      }
    }
    cur+=c
  }
  if(cur.trim()) out.push(cur.trim());
  return out;
}

// Minimal value parser (pragmatic)
function parseValue(raw:string): any {
  const t = raw.trim();
  if (t.startsWith('"') && t.endsWith('"')) return t.slice(1,-1);
  if (t.startsWith("//") && t.endsWith("//")){
    // choice //a//b// -> ["a","b"] with tag
    const inner = t.slice(2,-2);
    return { __choice: inner.split("//").map(x=>x.trim()) };
  }
  if (t.startsWith("[") && t.endsWith("]")){
    // array: split by top-level commas
    const inner = t.slice(1,-1);
    return splitTopLevelSlots(inner).map(parseValue);
  }
  if (t.startsWith("(") && t.endsWith(")")){
    const inner = t.slice(1,-1);
    return { __tuple: splitTopLevelSlots(inner).map(parseValue) };
  }
  if (t.startsWith("|") && t.endsWith("|")){
    const inner = t.slice(1,-1);
    return { __set: splitTopLevelSlots(inner).map(parseValue) };
  }
  // record like ident{...}
  const mrec = t.match(/^([A-Za-z_][A-Za-z0-9_]*)\s*\{([\s\S]*)\}$/);
  if (mrec){
    const kind = mrec[1];
    const body = mrec[2].trim().replace(/\}$/,'');
    const obj:any = { type: kind };
    for (const pair of splitTopLevelSlots(body)){
      const k = pair.split(":")[0]?.trim();
      const v = pair.slice(pair.indexOf(":")+1);
      if(k) obj[k]=parseValue(v)
    }
    return obj;
  }
  // map-like {k:v}
  if (t.startsWith("{") && t.endsWith("}")){
    const inner = t.slice(1,-1);
    const obj:any = {};
    for (const pair of splitTopLevelSlots(inner)){
      const k = pair.split(":")[0]?.trim();
      const v = pair.slice(pair.indexOf(":")+1);
      if(k) obj[k]=parseValue(v)
    }
    return obj;
  }
  // durations/time as strings for simplicity
  if (/^\d{4}-\d{2}-\d{2}(?:T[^\s]+)?$/.test(t)) return { __time: t };
  if (/^\d+(?:\.\d+)?[smhdw](?:\d+(?:\.\d+)?[smhdw])*$/.test(t)) return { __duration: t };

  // quantity like 2cm, 90C, 60%
  if (isQuantityToken(t)){
    const m = t.match(/^([-+]?\d+(?:\.\d+)?(?:e[-+]?\d+)?)([A-Za-z%°]+)$/);
    if(m){
      const value = Number(m[1]);
      const unit = m[2] === "%" ? "percent" : m[2];
      return { value, unit };
    }
  }
  const num = parseNumber(t);
  if (num!==null) return num;
  if (t==="true"||t==="false") return t==="true";
  return t; // ident fallback
}

function canonicalizeSlots(slots:Record<string,any>): Record<string,any> {
  const o:Record<string,any> = {};
  for (const k of CANONICAL_ORDER) if (slots[k]!==undefined) o[k]=slots[k];
  for (const k of Object.keys(slots)) if (!(CANONICAL_ORDER as readonly string[]).includes(k)) o[k]=slots[k];
  return o;
}

// Parse a single statement line -> {verb, mood, slots}
function parseStatement(line:string){
  const trimmed = line.trim();
  if(!trimmed) return null;
  // split trailing result hint -> ignore but keep in hint.then
  let base = trimmed; let hint: any = undefined;
  const arrowIdx = trimmed.indexOf("->");
  if (arrowIdx>=0){
    base = trimmed.slice(0,arrowIdx).trim();
    const thenPart = trimmed.slice(arrowIdx+2).trim();
    hint = { then: [ { raw: thenPart } ] };
  }
  const m = base.match(/^([A-Za-z_][A-Za-z0-9_]*)\s*\{([\s\S]*)\}\s*([\?\!\.]*)$/);
  if(!m) throw { code:"E001", hint:"parse-fail", got: line };
  const verb = m[1];
  if(!KNOWN_VERBS.has(verb)) throw { code:"E002", hint:"unknown-verb", got: verb };
  const body = m[2];
  const mood = (m[3] as Mood) || ".";
  const pairs = splitTopLevelSlots(body);
  const slots:Record<string,any> = {};
  for (const pair of pairs){
    const sep = pair.indexOf(":");
    if (sep<0) throw { code:"E001", hint:"slot-missing-colon", got: pair };
    const k = pair.slice(0,sep).trim();
    const v = parseValue(pair.slice(sep+1));
    slots[k]=v;
  }
  // safety barrier for !
  if (mood==='!'){
    const hasSafety = ("rule" in slots) || ("risk" in slots) || ("conf" in slots);
    if(!hasSafety) throw { code:"E013", hint:"unsafe-commit", got: line };
  }
  return { verb, mood, slots: canonicalizeSlots(slots), hint };
}

function stringifyCJON(a:any){
  return JSON.stringify(a,null,2);
}

function prettyFormat(lines:string[]): { ok:true, text:string } | { ok:false, error:any }{
  try{
    const out = lines.map(l=>{
      if(!l.trim()) return "";
      const s = parseStatement(l);
      if(!s) return "";
      return `${s.verb}{${Object.entries(s.slots).map(([k,v])=>`${k}:${formatVal(v)}`).join(", ")}}${s.mood}`
    }).join("\n");
    return { ok:true, text: out };
  }catch(e:any){
    return { ok:false, error: e };
  }
}

function formatVal(v:any): string {
  if (v && typeof v === 'object'){
    if (Array.isArray(v)) return `[${v.map(formatVal).join(", ")}]`;
    if ("__tuple" in v) return `(${(v.__tuple as any[]).map(formatVal).join(", ")})`;
    if ("__set" in v) return `|${(v.__set as any[]).map(formatVal).join(", ")}|`;
    if ("__choice" in v) return `//${(v.__choice as any[]).join("//")}//`;
    if ("__time" in v) return v.__time;
    if ("__duration" in v) return v.__duration;
    if ("type" in v){
      const { type, ...rest } = v as any;
      const inner = Object.entries(rest).map(([k,iv])=>`${k}:${formatVal(iv)}`).join(", ");
      return `${type}{${inner}}`;
    }
    if ("value" in v && "unit" in v){
      return v.unit==="percent" ? `${v.value}%` : `${v.value}${v.unit}`;
    }
    // plain map
    return `{${Object.entries(v).map(([k,iv])=>`${k}:${formatVal(iv)}`).join(", ")}}`;
  }
  if (typeof v === 'string'){
    if (/^[A-Za-z_][A-Za-z0-9_]*$/.test(v)) return v;
    return JSON.stringify(v);
  }
  if (typeof v === 'number' || typeof v === 'boolean') return String(v);
  return JSON.stringify(v);
}

function ailoToCJON(program:string){
  const lines = program.split(/\r?\n/).map(l=>l.replace(/#.*/, "").trim()).filter(Boolean);
  const actions = lines.map(parseStatement);
  return actions.map(a=>({
    version:"SCP 0.9-E",
    sr:{ verb:a!.verb, mood:a!.mood, slots:a!.slots },
    hint: a!.hint,
  }))
}

function cjonToAilo(cjonText:string){
  const data = tryJsonParse(cjonText);
  if(!data) throw new Error("Invalid JSON");
  const arr = Array.isArray(data) ? data : [data];
  const lines = arr.map(packet=>{
    const sr = packet.sr || packet;
    const verb = sr.verb; const mood = sr.mood || ".";
    const slots = canonicalizeSlots(sr.slots || {});
    return `${verb}{${Object.entries(slots).map(([k,v])=>`${k}:${formatVal(v)}`).join(", ")}}${mood}`
  });
  return lines.join("\n");
}

// ---------- UI ----------

const DEFAULT_EXAMPLE = `#! AILO 0.9 profile:strict
see{ag:bot obj:fridge rule:inventory}? # query
filter{obj:food rule:time<10m}.
decide{ag:planner obj://ramen//bibimbap to:meal rule:{health:0.6,taste:0.4} why:hurry conf:0.72}! -> act{ag:chef}
act{ag:arm1 obj:potato state:cut size:2cm with:{tool:knife} risk:{slip:0.1,burn:0.05} rule:guardOn when:{start:2025-10-25T09:00+09:00}}! -> check{rule:safe}`;

export default function AILOStudio(){
  const [src,setSrc] = useState<string>(DEFAULT_EXAMPLE);
  const [fmtErr,setFmtErr] = useState<any>(null);
  const [cjon,setCjon] = useState<string>("");
  const [hash,setHash] = useState<string>("");
  const [status,setStatus] = useState<string>("Idle");

  async function doFormat(){
    setFmtErr(null);
    const lines = src.split(/\r?\n/);
    const res = prettyFormat(lines);
    if(res.ok){ setSrc(res.text); setStatus("Formatted"); }
    else { setFmtErr(res.error); setStatus("Format error"); }
  }

  function doToCJON(){
    try{
      const packets = ailoToCJON(src);
      setCjon(stringifyCJON(packets));
      setStatus("CJON generated");
    }catch(e:any){ setFmtErr(e); setStatus("CJON error"); }
  }

  function doFromCJON(){
    try{
      const text = cjonToAilo(cjon);
      setSrc(text); setStatus("From CJON");
    }catch(e:any){ setFmtErr(e); setStatus("From CJON error"); }
  }

  async function doHash(){
    const payload = cjon || stringifyCJON(ailoToCJON(src));
    const h = await sha256Hex(enc(payload));
    setHash("sha3-256:"+h.slice(0,64));
    setStatus("Hashed");
  }

  function copy(text:string){ navigator.clipboard.writeText(text); }

  function download(name:string, body:string){
    const blob = new Blob([body],{type:"text/plain;charset=utf-8"});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a'); a.href=url; a.download=name; a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="w-full max-w-6xl mx-auto p-6 space-y-6">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">AILO–SCP v0.9-E Studio</h1>
          <p className="text-sm text-muted-foreground">Author · Lint · Format · CJON · Hash — single-file playground</p>
        </div>
        <div className="flex gap-2">
          <Button variant="secondary" onClick={()=>copy(src)}><Copy className="h-4 w-4 mr-2"/>Copy AILO</Button>
          <Button variant="secondary" onClick={()=>copy(cjon)} disabled={!cjon}><Copy className="h-4 w-4 mr-2"/>Copy CJON</Button>
          <Button onClick={()=>download("program.ailo",src)}><Download className="h-4 w-4 mr-2"/>.ailo</Button>
          <Button onClick={()=>download("packets.json", cjon || stringifyCJON(ailoToCJON(src)))}><Download className="h-4 w-4 mr-2"/>CJON</Button>
        </div>
      </header>

      <Card className="shadow-sm">
        <CardHeader className="pb-2">
          <CardTitle className="text-base flex items-center gap-2"><FileText className="h-4 w-4"/> Editor</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <Textarea value={src} onChange={e=>setSrc(e.target.value)} rows={12} className="font-mono text-sm"/>
          <div className="flex flex-wrap gap-2">
            <Button onClick={doFormat}><Sparkles className="h-4 w-4 mr-2"/>Format</Button>
            <Button variant="outline" onClick={doToCJON}><ArrowRight className="h-4 w-4 mr-2"/>To CJON</Button>
            <Button variant="outline" onClick={doFromCJON}><ArrowRight className="h-4 w-4 mr-2 rotate-180"/>From CJON</Button>
            <Button variant="secondary" onClick={doHash}><Hash className="h-4 w-4 mr-2"/>Hash</Button>
            <Badge variant={fmtErr?"destructive":"secondary"}>{fmtErr? `${fmtErr.code||"ERR"}: ${fmtErr.hint||fmtErr.message||"parse"}` : status}</Badge>
          </div>
          {fmtErr && (
            <div className="rounded-lg bg-destructive/10 border border-destructive/30 p-3 text-sm text-destructive">
              <div className="font-semibold mb-1">Validation Error</div>
              <pre className="whitespace-pre-wrap">{JSON.stringify(fmtErr,null,2)}</pre>
            </div>
          )}
        </CardContent>
      </Card>

      <div className="grid md:grid-cols-2 gap-4">
        <Card className="shadow-sm">
          <CardHeader className="pb-2"><CardTitle className="text-base">CJON Packets</CardTitle></CardHeader>
          <CardContent>
            <Textarea value={cjon} onChange={e=>setCjon(e.target.value)} rows={14} className="font-mono text-xs" placeholder="Click ‘To CJON’ to generate..."/>
          </CardContent>
        </Card>
        <Card className="shadow-sm">
          <CardHeader className="pb-2"><CardTitle className="text-base">Meta</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center gap-2"><span className="text-sm text-muted-foreground">Packet Hash</span>{hash && <Badge>{hash}</Badge>}</div>
            <Separator/>
            <div className="text-xs text-muted-foreground leading-relaxed">
              <p>• Canonical slot order: {CANONICAL_ORDER.join(", ")}</p>
              <p>• Safety gate: commits <code>! </code> require one of <code>rule</code>, <code>risk</code>, <code>conf</code> → else E013.</p>
              <p>• Unknown verbs → E002. Minimal parser aims for v0.9-E examples; not a full EBNF.</p>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card className="shadow-sm">
        <CardHeader className="pb-2"><CardTitle className="text-base">Quick Examples</CardTitle></CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-3 gap-3 text-xs font-mono">
            <Example code={`see{obj:fridge rule:inventory}?`}/>
            <Example code={`decide{ag:planner obj://ramen//bibimbap to:meal rule:{health:0.6,taste:0.4} why:hurry conf:0.72}! -> act{ag:chef}`}/>
            <Example code={`act{ag:arm1 obj:apple state:slice size:1cm rule:safe risk:{cut:0.05} conf:0.96 with:{tool:knife}}!`}/>
          </div>
        </CardContent>
      </Card>

      <footer className="pt-2 pb-8 text-xs text-muted-foreground">
        MIT © 2025 sorihanul • AILO–SCP v0.9-E Studio • Single-file TSX
      </footer>
    </div>
  )
}

function Example({code}:{code:string}){
  const { set } = React.useContext(ExampleBus);
  return (
    <button onClick={()=>set(code)} className="text-left rounded-xl p-3 bg-muted hover:bg-muted/80 transition border border-border">
      {code}
    </button>
  )
}

const ExampleBus = React.createContext<{ set: (code:string)=>void }>({ set: ()=>{} });

// Provide ExampleBus via wrapper when embedding in an app
export function AILOStudioProvider(){
  const [code,setCode] = useState<string>(DEFAULT_EXAMPLE);
  return (
    <ExampleBus.Provider value={{ set: (c)=>{
      const ta = document.querySelector<HTMLTextAreaElement>('textarea');
      if(ta){ ta.value = c; ta.dispatchEvent(new Event('input',{bubbles:true})) }
    }}}>
      <AILOStudio/>
    </ExampleBus.Provider>
  )
}
