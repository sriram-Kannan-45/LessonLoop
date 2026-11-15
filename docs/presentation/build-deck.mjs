// Run with the bundled Codex presentation runtime; see README.md in this directory.
import fs from 'node:fs/promises';
import path from 'node:path';
import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';
import { slides, demoScript } from './deck-content.mjs';

const workspaceDir = process.env.LESSONLOOP_WORKSPACE || 'D:/LessonLoop';
const runtime = process.env.RUNTIME_NODE_MODULES;
const skill = process.env.PRESENTATIONS_SKILL_DIR;
if (!runtime || !skill) throw new Error('Set RUNTIME_NODE_MODULES and PRESENTATIONS_SKILL_DIR.');
const require = createRequire(path.join(runtime, '__loader.cjs'));
const { Presentation, PresentationFile } = await import(pathToFileURL(require.resolve('@oai/artifact-tool')).href);
const { finalizePresentation } = await import(pathToFileURL(path.join(skill, 'container_tools/artifact_tool_utils.mjs')).href);
const build = path.join(workspaceDir, '.cache/presentation-build');
const out = path.join(workspaceDir, 'artifacts/presentation');
await fs.mkdir(build, {recursive:true}); await fs.mkdir(out, {recursive:true});
const p = Presentation.create({slideSize:{width:1280,height:720}});
const colors={ink:'#142438',teal:'#0B756D',muted:'#526276',paper:'#F8FAFC',mint:'#92E5C3',white:'#FFFFFF'};
const fontPolicy={basis:'design',families:['Arial','Consolas']};
function text(s,value,x,y,w,h,size=28,color=colors.ink,bold=false,font='Arial') {
  const box=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
  box.text=value; box.text.style={typeface:font,fontSize:size,color,bold,autoFit:'none',wrap:'square',insets:0};
  return box;
}
function base(d,i) {
  const s=p.slides.add(); s.background.fill=colors.paper;
  text(s,d.title,64,53,1152,95,44,colors.ink,true);
  text(s,String(i+1).padStart(2,'0'),1180,675,45,25,16,colors.muted);
  s.speakerNotes.text=`TIMING: ${d.time}\n\n${d.notes}\n\nSources: ${d.source}`;
  return s;
}
function connect(s,a,b,fromSide='right',toSide='left',kind='straight',color=colors.teal) {
  return s.shapes.connect(a,b,{kind,fromSide,toSide,line:{fill:color,width:2.5},tail:{type:'triangle',width:'med',length:'med'}});
}
for (const [i,d] of slides.entries()) {
  const s=base(d,i);
  if (d.kind==='cover') {
    s.background.fill=colors.ink;
    // All foreground content remains editable text.
    s.shapes.items[0].text='';
    text(s,'LessonLoop',70,210,1110,115,88,colors.mint,true);
    text(s,d.subtitle,75,350,1090,82,38,colors.white);
    text(s,'GenAI Engineer  /  Content Systems',75,485,1000,50,26,'#B9C8D9');
    text(s,'Planning, implementation and product walkthrough',75,543,1100,44,26,'#B9C8D9');
  } else if (d.kind==='rows') {
    d.rows.forEach(([n,label,detail],j)=>{
      const y=205+j*132;
      text(s,n,64,y,130,65,46,colors.teal,true);
      text(s,label,220,y,340,65,30,colors.ink,true);
      text(s,detail,590,y+2,610,90,27,colors.muted);
    });
  } else if (d.kind==='list' || d.kind==='terms') {
    const step=d.items.length===6?72:d.items.length===5?88:105;
    d.items.forEach(([label,detail],j)=>{
      const y=180+j*step;
      text(s,label,65,y,438,65,d.kind==='terms'?30:27,colors.teal,true,d.kind==='terms'&&j>2?'Consolas':'Arial');
      text(s,detail,535,y,670,68,27,colors.ink);
    });
    if(d.foot) text(s,d.foot,65,625,1125,42,20,colors.muted);
  } else if (d.kind==='graph') {
    const names=['load_context','generate_lesson','validate_structure','evaluate_lesson','persist_final_result'];
    const lines=['Sources and rules','Create or revise','Schema and citations','Content checks','Save final status'];
    const nodes=names.map((name,j)=>{
      const x=60+j*232;
      const shape=s.shapes.add({geometry:'rect',position:{left:x,top:220,width:200,height:105},fill:j===4?colors.teal:colors.ink,line:{fill:'none',width:0}});
      shape.text=name.replace('_','_\n');
      shape.text.style={typeface:'Consolas',fontSize:22,color:colors.white,alignment:'center',verticalAlignment:'middle',insets:8};
      text(s,lines[j],x,160,205,53,22,colors.muted);
      return shape;
    });
    for(let j=0;j<4;j++)connect(s,nodes[j],nodes[j+1]);
    // Explicit native connector segments preserve the return route in PowerPoint.
    const leg=(position,arrow=false)=>s.shapes.add({geometry:'connector',kind:'straight',position,line:{fill:colors.teal,width:2.5},...(arrow?{head:{type:'triangle',width:'med',length:'med'}}:{})});
    leg({left:856,top:325,width:0,height:50});
    leg({left:392,top:375,width:464,height:0});
    leg({left:392,top:325,width:0,height:50},true);
    text(s,'Fail and drafts remain',325,390,620,60,30,colors.teal,true);
    text(s,'Pass or draft limit reached',885,345,325,72,22,colors.muted);
    text(s,'All mandatory checks pass: APPROVED',65,503,1140,60,31,colors.ink,true);
    text(s,'Unresolved after draft 3: NEEDS_REVIEW',65,570,1140,60,29,colors.muted);
  } else if (d.kind==='code') {
    d.code.forEach((line,j)=>text(s,line,65,180+j*38,1150,37,24,j===5||j===8?colors.teal:colors.ink,j===5||j===8,'Consolas'));
    text(s,'Equivalent excerpt based on backend/app/workflow.py',65,628,1120,36,20,colors.muted);
  } else if (d.kind==='commits' || d.kind==='history') {
    const step=d.kind==='history'?57:83;
    d.rows.forEach(([sha,label],j)=>{
      const y=178+j*step;
      text(s,sha,65,y,d.kind==='history'?170:330,50,d.kind==='history'?25:25,colors.teal,true,'Consolas');
      text(s,label,d.kind==='history'?255:410,y,d.kind==='history'?950:790,66,d.kind==='history'?25:27,colors.ink);
    });
    if(d.foot)text(s,d.foot,65,627,1125,42,19,colors.muted);
  } else if (d.kind==='demo') {
    d.items.forEach(([label,detail],j)=>{text(s,label,65,190+j*130,480,55,30,colors.teal,true);text(s,detail,65,247+j*130,480,80,25,colors.ink);});
    const bytes=await fs.readFile(path.join(out,'product.png'));
    s.images.add({blob:bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength),contentType:'image/png',alt:'Actual approved RAG run in the local LessonLoop app',fit:'contain',position:{left:625,top:170,width:575,height:445}});
  } else if (d.kind==='status') {
    text(s,'133',65,185,400,115,88,colors.teal,true);text(s,'backend tests passed',65,309,470,55,28);
    text(s,'44',650,185,400,115,88,colors.teal,true);text(s,'browser tests passed',650,309,500,55,28);
    text(s,'Pending acceptance',65,426,1130,50,31,colors.ink,true);
    text(s,'Qualifying live learning and later reuse\nCurrent calibration and live Tamil validation\nPublic document and face-visible video links',65,493,1130,145,27,colors.muted);
  }
  const file=await p.export({slide:s,format:'png',scale:1});
  await fs.writeFile(path.join(build,`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await file.arrayBuffer()));
}
const candidatePath=path.join(build,'candidate.pptx');
await (await PresentationFile.exportPptx(p)).save(candidatePath);
const finalPath=path.join(out,process.env.DECK_OUTPUT || 'LessonLoop-Walkthrough.pptx');
await finalizePresentation({workspaceDir,candidatePath,finalPath,pythonExecutable:process.env.RUNTIME_PYTHON,
  integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),
  layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),
  layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit'],
  requiredNativeTableOwnerSlides:[],fontPolicy,verifyArtifactToolImport:true,
  receiptPath:path.join(build,path.basename(finalPath)+'.validation.json')});
// Optional PDF preview can be produced with native PowerPoint if this runtime lacks PDF fonts.
const script=demoScript+'\n\n# Slide speaker notes\n\n'+slides.map((s,i)=>`## Slide ${i+1}  ${s.title}\n\nTiming: ${s.time}\n\n${s.notes}\n\nSources: ${s.source}`).join('\n\n');
await fs.writeFile(path.join(workspaceDir,'docs/DEMO_PRESENTATION_SCRIPT.md'),script);
console.log(JSON.stringify({slides:p.slides.items.length,finalPath}));
