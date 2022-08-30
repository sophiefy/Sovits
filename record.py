Skip to content
Search or jump to…
Pull requests
Issues
Marketplace
Explore
 
@Francis-Komizu 
Francis-Komizu
/
StarGANv2-VC
Public
forked from yl4579/StarGANv2-VC
Code
Pull requests
Actions
Projects
Wiki
Security
Insights
Settings
StarGANv2-VC/record.py /
@Francis-Komizu
Francis-Komizu Update record.py
Latest commit 555e3ff 6 days ago
 History
 1 contributor
120 lines (101 sloc)  3.07 KB

"""
ref: https://ricardodeazambuja.com/deep_learning/2019/03/09/audio_and_video_google_colab/
"""
import io
import ffmpeg
import librosa
import numpy as np
from base64 import b64decode
from scipy.io.wavfile import read
from IPython.display import HTML, Audio
from google.colab.output import eval_js

AUDIO_HTML = """
<script>
var my_div = document.createElement("DIV");
var my_p = document.createElement("P");
var my_btn = document.createElement("BUTTON");
var t = document.createTextNode("Press to start recording");
my_btn.appendChild(t);
//my_p.appendChild(my_btn);
my_div.appendChild(my_btn);
document.body.appendChild(my_div);
var base64data = 0;
var reader;
var recorder, gumStream;
var recordButton = my_btn;
var handleSuccess = function(stream) {
	gumStream = stream;
	var options = {
		//bitsPerSecond: 8000, //chrome seems to ignore, always 48k
		mimeType : 'audio/webm;codecs=opus'
		//mimeType : 'audio/webm;codecs=pcm'
	};						
	//recorder = new MediaRecorder(stream, options);
	recorder = new MediaRecorder(stream);
	recorder.ondataavailable = function(e) {						
		var url = URL.createObjectURL(e.data);
		var preview = document.createElement('audio');
		preview.controls = true;
		preview.src = url;
		document.body.appendChild(preview);
		reader = new FileReader();
		reader.readAsDataURL(e.data); 
		reader.onloadend = function() {
			base64data = reader.result;
			//console.log("Inside FileReader:" + base64data);
		}
	};
	recorder.start();
	};
recordButton.innerText = "Recording... press to stop";
navigator.mediaDevices.getUserMedia({audio: true}).then(handleSuccess);
function toggleRecording() {
	if (recorder && recorder.state == "recording") {
			recorder.stop();
			gumStream.getAudioTracks()[0].stop();
			recordButton.innerText = "Saving the recording... pls wait!"
	}
}
// https://stackoverflow.com/a/951057
function sleep(ms) {
	return new Promise(resolve => setTimeout(resolve, ms));
}
var data = new Promise(resolve=>{
//recordButton.addEventListener("click", toggleRecording);
recordButton.onclick = ()=>{
toggleRecording()
sleep(2000).then(() => {
	// wait 2000ms for the data to be available...
	// ideally this should use something like await...
	//console.log("Inside data:" + base64data)
	resolve(base64data.toString())
});
}
});
			
</script>
"""

def get_audio():
	display(HTML(AUDIO_HTML))
	data = eval_js("data")
	binary = b64decode(data.split(',')[1])
	
	process = (ffmpeg
		.input('pipe:0')
		.output('pipe:1', format='wav')
		.run_async(pipe_stdin=True, pipe_stdout=True, pipe_stderr=True, quiet=True, overwrite_output=True)
	)
	output, err = process.communicate(input=binary)
	
	riff_chunk_size = len(output) - 8
	# Break up the chunk size into four bytes, held in b.
	q = riff_chunk_size
	b = []
	for i in range(4):
			q, r = divmod(q, 256)
			b.append(r)

	# Replace bytes 4:8 in proc.stdout with the actual size of the RIFF chunk.
	riff = output[:4] + bytes(b) + output[8:]
	sr, audio = read(io.BytesIO(riff))
	audio = audio/max(abs(audio))
	audio = librosa.resample(audio, sr, 16000)
	audio, _ = librosa.effects.trim(audio)
	audio = (32767*audio).astype(np.int16)
	return audio
Footer
© 2022 GitHub, Inc.
Footer navigation
Terms
Privacy
Security
Status
Docs
Contact GitHub
Pricing
API
Training
Blog
About
