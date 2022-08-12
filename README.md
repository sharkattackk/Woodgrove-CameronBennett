# Woodgrove Documentation- Cameron Bennett
<p>I joined the software devlopment team at Woodgrove tech on the 2nd of may 2022. My focus was placed on the AI image processing solution which offers clients with valuable data and information related to their extracted rock samples. Woodgrove's software was responsible for processing input from cameras placed towards a conveyor belt which moved rock samples from the earth.</p>
<p>The issue was that these very high intensity and strenuous calculations require a centralized and powerful computing system. This causes overload and thus ineficiencies in our servers. This document features a description of how this issue was approached and what is required to optimize this area of Woodgrove's solutions going forward.</p>
<hr>
<h4>Table of Contents</h4>
<ul>
    <li><a href="#Jetson">Jetson Xavier NX</a></li>
    <li><a href="#Dexi-SD">Dexi-Ned Capable SD Image</a></li>
    <li><a href="#Nuc">Intel NUC</a></li>
    <li><a href="#ONVIF">ONVIF Device Manager</a></li>
    <li><a href="#OVMS">Open Vino Model Server</a></li>
    <li><a href="#Dexi-NUC">Dexi-Ned Capable intel NUC</a></li>
    <li><a href="#next">Next Steps</a></li>
    <li><a href="#resources">Useful Resources</a></li>
</ul>
<hr>

<h4 id="Jetson">Jetson Xavier NX</h4>
<p>On my very first day at Woodgrove I was presented with the first possible solution to this centralized server overload. This soution was the Jetson Xavier NX, pictured below.</p>
<img src= "https://hackster.imgix.net/uploads/attachments/1120136/_irA6vV6H9j.blob?auto=&format=jpg" style="height:300px;width:280.9px">
<p>This device is an impressive computer, featuring 384-core NVIDIA GPU and 48 Tensor cores as well as 6-core 64 bit NVIDIA CPU all with only 70mm x 40mm to work with. The device is specifically designed for running inference on videos and computer vision, hence its powerful GPU. The first tests I ran on this device were trying out different pretrained AI models from different providers such as jetson-inference and yolov5. These tests were to confirm the jetsons ability to handle live stream image processing and to determine if it would be able to handle our tasks.</p>
<p>Below is a screen capture of the output running yolov5 object detection software. This was operating at nearly 30 fps and very smoothly.</p>
<img src="https://user-images.githubusercontent.com/106261884/182909473-900ac5ba-027c-4b01-b13a-acf7893ebaf1.png" style="height:300px;width:280.9px">
<p>Though this was a great sign, the board proved to be inadequete for the tasks Woodgrove would ask of it. </p>
<hr>
<h4 id="Dexi-SD">Dexi-Ned Capable SD Image</h4>
<p>Numerous re-flashes of the SD card were required to untangle to various versions of Dexi-Ned's dependencies. To save the next developer the time of installing and organizing <a href="https://www.python.org/downloads/release/python-370/g">Python 3.7</a>, <a href="https://pytorch.org/">Pytorch >=1.4 <= 1.9</a>, <a href="https://pypi.org/project/opencv-python/">OpenCV</a>, <a href="https://matplotlib.org/3.1.1/users/installing.html">Matplotlib</a>, and <a href="https://kornia.github.io/">Kornia</a>. Important to note that this OpenCV is bootable on the Jetson and is capable of running any OpenCV based programs for image processing. This is version 4.4.1 of OpenCV. I have provided a Dexi-Ned capable SD image with all of these dependencies isntalled. To get this image onto the boards operating system, simply flash the SD card using <a href="https://www.balena.io/etcher/">belena etcher</a> and remember to wipe the SD card prior.</p>
<p>Below is a sample output of running the main.py file from the <a href="https://github.com/xavysp/DexiNed">Dexi-Ned Github repository</a> operating on this SD image.</p>
<img src="https://user-images.githubusercontent.com/106261884/182916786-07e25bfe-f4e2-4ec7-a1d0-c77a19c827b5.png" style="height:300px;width:280.9px">
<p>Since video processing posed many challenges due to the ubuntu UI, this image was the final attempt made on the Jetson Board before being deemed less viable than alternatives. These alternatives are looked at in the next sections.</p>
<hr>
<h4 id="Nuc">Intel Nuc</h4>
<p>The next option to achieve the same goal as the Jetson is the Intel NUC. The version we worked with was the Intel NUC 10 Performance NUC10i7FNH. This device is very similar in size to the Jetson however it features it's own housing. The exterior of the board has 3 USB ports, an HDMI port, 19v Power adapter and an SD card port. This is useful for attacthing Input/Output devices such as a keyboard, mouse, and monitor allowing the NUC to behave exactly like any desktop computer. below is an image of the Intel NUC we initially worked on.</p>
<img src="https://user-images.githubusercontent.com/106261884/182933064-387f70f9-d18b-4108-a8b2-bd8b57a32eb5.jpg">
<p>Inside the NUC we have a 10th gen intel core, i7 processor, 256 GB NVMe SSD, 1TB HDD, and 16GB RAM. All very impressive satistics even for a full size PC. In addition, unline the Jetson, this device supports Windows 10 Home, allowing for familiar and easy user interface.</p>
<p>When you get access to a brand new NUC and Windows 10 is set up, the first steps you should take are install and configure an ideal version of python and <a href="https://www.docker.com/">Download Docker</a></p>
<hr>
<h4 id="ONVIF">ONVIF Device Manager</h4>
<p>ONVIF device manager is another software that should be installed and configured on the board. It is a protocol that can connect to any any IP camera on that network, regardless of company. Simply boot up the program, and a list of all IP cameras which are present on the network will appear in a list. The protocol allows for many specifications including zooming in and out.</p>
<p> A detailed description can be found at this <a href="https://www.youtube.com/watch?v=UC8oGdfJkdI">youtube video</a>.
<p>the ONVIF UI is shown below</p>
<img src="https://user-images.githubusercontent.com/106261884/183118988-eaaaec3e-0501-4929-9145-20e049b57373.png" style="height:300px;width:280.9px">
<hr>
<h4 id="OVMS">Open Vino Model Server</h4>
<p>The Open Vino Model Server opened up several doors and proved to be the most important piece of the puzzle. OVMS is a docker image which can be launched using a <a href="https://www.docker.com/">docker</a> container. This launches a server with a few customizeable traits. These traits consist of information about a model. This model can be any .onnx, .xml, .pth model that can process video streams through neural networks in a contained virtual environment of the OV model server.</p>
<p>To launch the docker container with the OVMS docker image, run the following command.</p>

``` 
docker run -d -v /c/Users/Matin/model:/models -p 9000:9000 openvino/model_server:latest --model_path /models --model_name DexiNed-Woodgrove --port 9000 --shape auto
```  
<p>Please see the following section to ensure that the correct onnx or xml model is in fact located in /c/Users/Matin/model.</p>
<p>This single command will create a model server on port 9000 where any neural network model, in this case DexiNed, will be able loaded in. </P>
<hr>
<h4 id="Dexi-NUC">Dexi-Ned Capable intel NUC</h4>
<p>The model which gave a successful result when loaded into the OVMS docker can be downloaded here at <a href="https://drive.google.com/file/d/1aDOetxvIos8pUO_Q3cgRm78PiMYmYI0B/view?usp=sharing">dexinedWGT.ONNX</a>. This model must be placed in a folder titled /c/Users/Matin/model as previously mentioned.</p>
<p>Once you run the command in the previous section, you now have a model server loaded with the above DexiNed model and are ready to run inference on an image, video, or livestream. The next step is to run the dexined-woodgrove.py file found above with a few specified parameters.</p>

```
python dexined-woodgrove.py -n dexined-woodgrove -l input.1 -o 502 -d 352 -c 1 -i localhost -p 9000
```
<p>Here the '-n' argument is the model name. Must be the same as the "--model_name" argument passed when launching the docker container. The "-l" and "-o" are the input and output layers respetively and can be confirmed by opening the model in a visualizer such as <a href="https://netron.app/">Netron</a>. The -d argument is the shape of frame expected by the model. This can also be confirmed by opening the model on Netron. This is one area where there is need for improvement because an inreased frame size leads to a mroe accurate segmentation. The "-c" argument is simply the number of camera inputs to be expected, and can be replaced or work in parallel with "-f" which must be followed by a path to a video file. Finally, the "-i" and "-p" arguments point the program to the desired model server, which was also defined when launching the server.</p>

<p>If all excecuted correctly, you should be seeing a 352 x 352 window titled "dexi stream" which should show the output of your camera with all lines/edges in the frame closer to white(255) while the rest closer to black(0). If so, you have successfully run Dexi-Ned inference on a livestream through the intel NUC. This is a great first step, and now all thats required is optimization, performance enhancements, and further specifications to create a viable solution that Woodgrove can offer clients.</p>
<hr>
<h4 id="next">Next Steps</h4>
<p>The end product should incorporate the woodgrove crafted software which is based on Dexi-Ned, which can distinguish between fine rocks, connected rocks, and single rocks. This solution should also offer strong performance comparable to that of the desktop computer currently in use.</p>
<p>Below captures the desired output after implementing Woodgroves software</p>
<img src="https://user-images.githubusercontent.com/106261884/184170372-2c40c3e8-70f6-4e64-a321-c5949b32929a.PNG" style="height:300px;width:280.9px">
<p>The next step in producing this result are to enhance the performance of the current DexiNed stream we have achieved. There are several ways to approach this task with the most signifacen change occuring when the program can switch from the CPU to the iGPU.</p>
<hr>
<h4 id="resources">Useful Resources</h4>
<a href="https://github.com/openvinotoolkit/model_server">Open Vino Model Server Github</a>
<a href="https://github.com/xavysp/DexiNed">DexiNed Github</a>
