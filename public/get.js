function download(fileUrl, fileName) {
  var a = document.createElement("a");
  a.href = fileUrl;
  a.setAttribute("download", fileName);
  a.click();
}

function loadContent () {
    fetch("/index")
   
    .then((result) => {
      if (result.status != 200) { throw new Error("Bad Server Response"); }
      return result.text();
    })
   
    .then((content) => {
      console.log(content)
      document.getElementById("content").innerHTML = content;
    })
   
    .catch((error) => { console.log(error); });
}

function submit() {
    document.getElementById("main").style.display = "none";
    document.getElementById("loading").style.display = "block";
    const speaker = document.getElementById("dropdown").value;
    const text = document.getElementById("text").value;
    
    fetch("/?dropdown="+speaker+"&text="+text).then((result) => {
      if (result.status != 200) {
        document.getElementById("loading").style.display = "none";
        document.getElementById("error").style.display = "block";
      } else {
        download("/audio", "MyAudio.wav");

        document.getElementById("loading").style.display = "none";
        document.getElementById("finished").style.display = "block";
      }
    })
}

function refresh() {
  document.getElementById("main").style.display = "block";
  document.getElementById("finished").style.display = "none";
  document.getElementById("error").style.display = "none";
  document.getElementById("loading").style.display = "none";
}

loadContent()