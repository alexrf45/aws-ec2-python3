curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

sudo wget https://github.com/99designs/aws-vault/releases/download/v6.6.0/aws-vault-linux-amd64 -O /usr/local/bin/aws-vault && \
	sudo chown $USER:$USER /usr/local/bin/aws-vault && \
	chmod +x /usr/local/bin/aws-vault
	
sudo apt-get install rng-tools -y && \
	sudo rngd -r /dev/urandom \

sudo apt-get install pass -y

gpg --batch --gen-key <<EOF
Key-Type: 1
Key-Length: 2048
Subkey-Type: 1
Subkey-Length: 2048
Name-Real: EC2-User
Name-Email: test@test.com
Expire-Date: 0
EOF

export GPGID=$(gpg --list-secret-keys | awk  '{ print $1 }' | head -n 4 | cut -f 1 -d '/' | cut -f 1 -d '-' | grep -i 5)


pass init $GPGID


pip install boto3 boto3auth

