const chat=document.getElementById("chat");
const message=document.getElementById("message");
const send=document.getElementById("send");
const fileInput=document.getElementById("fileInput");
const documents=document.getElementById("documents");
let sessionId=localStorage.getItem("support_session")||"";

function addMessage(text,type,sources=[],escalated=false){
    const row=document.createElement("div");
    row.className=`message ${type}`;
    const bubble=document.createElement("div");
    bubble.className="bubble";
    bubble.textContent=text;
    row.appendChild(bubble);
    if(type==="assistant" && sources.length){
        const source=document.createElement("div");
        source.className="source";
        source.textContent=`Sources: ${sources.join(", ")}`;
        bubble.appendChild(document.createElement("br"));
        bubble.appendChild(source);
    }
    if(escalated){
        const source=document.createElement("div");
        source.className="source";
        source.textContent="Escalation recommended";
        bubble.appendChild(document.createElement("br"));
        bubble.appendChild(source);
    }
    chat.appendChild(row);
    chat.scrollTop=chat.scrollHeight;
}

async function sendMessage(){
    const text=message.value.trim();
    if(!text)return;
    const welcome=document.querySelector(".welcome");
    if(welcome)welcome.remove();
    addMessage(text,"user");
    message.value="";
    message.style.height="auto";
    send.disabled=true;
    try{
        const res=await fetch("/api/chat",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({message:text,session_id:sessionId})});
        const data=await res.json();
        if(!res.ok)throw new Error(data.detail||"Request failed");
        sessionId=data.session_id;
        localStorage.setItem("support_session",sessionId);
        addMessage(data.answer,"assistant",data.sources,data.escalated);
    }catch(error){
        addMessage("Something went wrong. Please try again.","assistant");
    }finally{send.disabled=false;message.focus()}
}

send.addEventListener("click",sendMessage);
message.addEventListener("keydown",e=>{if(e.key==="Enter"&&!e.shiftKey){e.preventDefault();sendMessage()}});
message.addEventListener("input",()=>{message.style.height="auto";message.style.height=Math.min(message.scrollHeight,120)+"px"});
document.querySelectorAll(".suggestions button").forEach(button=>button.addEventListener("click",()=>{message.value=button.textContent;sendMessage()}));

async function loadDocuments(){
    const res=await fetch("/api/documents");
    const data=await res.json();
    documents.innerHTML="";
    if(!data.documents.length){
        documents.innerHTML='<div class="doc">No documents uploaded</div>';
        return;
    }
    data.documents.forEach(doc=>{
        const item=document.createElement("div");
        item.className="doc";
        item.textContent=doc.name;
        documents.appendChild(item);
    });
}

fileInput.addEventListener("change",async()=>{
    const file=fileInput.files[0];
    if(!file)return;
    const form=new FormData();
    form.append("file",file);
    const res=await fetch("/api/upload",{method:"POST",body:form});
    const data=await res.json();
    if(!res.ok){alert(data.detail||"Upload failed");return}
    await loadDocuments();
    fileInput.value="";
});

loadDocuments();
