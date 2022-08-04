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
</ul>

<h4 id="Jetson">Jetson Xavier NX</h4>
<p>On my very first day at Woodgrove I was presented with the first possible solution to this centralized server overload. This soution was the Jetson Xavier NX, pictured below.</p>
<img src= "https://hackster.imgix.net/uploads/attachments/1120136/_irA6vV6H9j.blob?auto=&format=jpg" style="height:300px;width:280.9px">
<p>This device is an impressive computer, featuring 384-core NVIDIA GPU and 48 Tensor cores as well as 6-core 64 bit NVIDIA CPU all with only 70mm x 40mm to work with. The device is specifically designed for running inference on videos and computer vision, hence its powerful GPU</p>
<a href="https://user-images.githubusercontent.com/106261884/182909473-900ac5ba-027c-4b01-b13a-acf7893ebaf1.png">here</a>


<hr>
<h4 id="Dexi-SD">Dexi-NedCapable SD Image</h4>

<hr>
<h4 id="Nuc">Intel Nuc</h4>


<hr>
<h4 id="ONVIF">ONVIF Device Manager</h4>


<hr>
<h4 id="OVMS">Open Vino Model Server</h4>



<hr>
<h4 id="Dexi-NUC">Dexi-Ned Capable intel NUC</h4>
The model which gave a successful result when loaded into the OVMS docker can be downloaded here at <a href="https://drive.google.com/file/d/1aDOetxvIos8pUO_Q3cgRm78PiMYmYI0B/view?usp=sharing">dexinedWGT.ONNX</a>. This model must be placed in a folder titled 


<hr>
