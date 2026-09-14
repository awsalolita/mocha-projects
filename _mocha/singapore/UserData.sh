#### this will run every-time in ec2 #### 
#### becareful to remove it if not idempotence ####

Content-Type: multipart/mixed; boundary="//"
MIME-Version: 1.0

--//
Content-Type: text/cloud-config; charset="us-ascii"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Content-Disposition: attachment; filename="cloud-config.txt"

#cloud-config
cloud_final_modules:
- [scripts-user, always]

--//
Content-Type: text/x-shellscript; charset="us-ascii"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Content-Disposition: attachment; filename="userdata.txt"
#!/bin/bash
echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIMMYdrgua7q6tNFaZEKP44jQxJiDYe/nBV+GWL/6+mYP Client@DESKTOP-RKTMC3T" >> /home/ec2-user/.ssh/authorized_keys 
sudo service sshd restart 