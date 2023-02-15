**Disclaimer** \
The distributed-file-backup repo is a personal project by looseMole and TidosDK, and is not intended for professional use. The 
software is provided as-is, and no warranties of any kind is provided if someone were to run the software within. For a more legal wording, see the projects license document.

**Description** \
The purpose of the program is to be able to back up locally stored files - compiled as well as plaintext - on the internet
semi-automatically and for free. To accomplish this, the software encrypts the file
locally, before uploading it to one, out of a range of websites, which offer free APIs for file-hosting. The 
download URLs and associated information is then stored on the user's device, and the validity of these links can then be checked 
regularly. If the files are to not be present at one of the sites, the program asks the user whether they want it to download it from one of the
other potential sites (provided the file cannot be found locally), and then attempt to re-upload it.

**Known Restrictions**
* File size: Because of the way the files are loaded during encryption and upload, the file size of these operations are limited by the memory (RAM) of the computer performing the task.
* Few (but good) servers: While this software seems to support quite a few different file-hosts, their similar layout and choice of name-servers suggest that the sites might share the same server-infrastructure. As a result, if one website's servers become inaccessible, it is likely that all of them will.

**Features We Are Hoping To Add**
* Upload to multiple different servers at once.
* A GUI (Graphical User Interface).
* Multiple encryption options.

\
**Currently supported sites**
* https://anonfiles.com
* https://bayfiles.com
* https://letsupload.cc
* https://filechan.org
* https://openload.cc
* https://megaupload.nz
* https://share-online.is
* https://vshare.is
* https://hotfile.io
* https://rapidshare.nu
* https://lolabits.se
* https://upvid.cc

\
**Sites to add to list**
* https://gofile.io
