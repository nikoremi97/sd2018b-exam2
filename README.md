# sd2018b-exam2
**Icesi University**  
**Course:** Distributed Systems   
**Professor:** Daniel Barragán C.  
**Subject:** Artifact building for Continous Delivery  
**Email:** daniel.barragan at correo.icesi.edu.co  
**Student:** Alejandro Bueno C.  
**Student ID:** A00335472  
**Git URL:** https://github.com/abc1196/sd2018b-exam2.git  

### Expected results
* Develop artifact automatic building for Continous Delivery  
* Use libraries of programming languages to perform specific tasks   
* Diagnose and execute the needed actions to achieve a stable infrastructure  

### Used technologies
* Docker  
* CentOS7 Box
* Github Repository
* Python3
* Python3 Libraries: Flask, Fabric
* Ngrok  

### Infrastructure diagram  
The desired infrastructure to deploy consists in three Docker Containers and one Docker Client with the following settings:

* Python:3.6-slim CI Server: this CT has a Flask application with and endpoint using RESTful architecture best practices. The endpoint has the following logic:   
  * A Webhook attached to a Pull Request triggers the endpoint.  
  * The endpoint reads the Pull Request content and validates if the PR is mergedd  
  * If merged, via the Docker Python SDK, the endpoint runs the required commands to build the Docker Artifact and push it to the local registry.  
* wernight/ngrok Ngrok: this CT creates a temporary public domain name to expose the CI Server's endpoint.  
* registry Registry: this CT is a private local registry where the created artifacts will be pushed.  
* Windows 10 Home Docker Client: this Docker Client will be used to pull the private registry's artifacts. 


![][1]  
**Figure 1**. Deploy Diagram  

### Issues  

### References  


[1]: images/deploy_diagram.png    
