fabfiles
========

My Fabric scripts for deployment.

Fabric is a great way of running procedures on remote server, as well as your local machine. Yet powerful since they are merely python scripts. I find it way easier and maintanable then writing bash scripts. 

These scripts asumes that you use Mac OSX as your development environment and a debian based linux distro (i.e. ubuntu) as your server environment.  

I couldn't decide on the organization of my fabfiles yet. There are different server environments and needs for each project. 
Thus my first reaction is to create a fabfile for each environment, along with a base fabfile class to maintain them. 
But since the scripts do trivial stuff (for now), I decided to put them in one place, organize them in a neat naming convention (underscore server name) 
