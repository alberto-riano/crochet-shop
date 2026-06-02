🚀 Deploy Django en AWS EC2
Guía completa para desplegar una aplicación Django en producción con AWS EC2, dominio propio y SSL.

📋 Stack
Servidor: AWS EC2 (Ubuntu 22.04/26.04)
Web server: Nginx
App server: Gunicorn
SSL: Certbot (Let's Encrypt)
Media files: AWS S3
Dominio: Namecheap
1. Comprar dominio en Namecheap
Ir a namecheap.com
Buscar el dominio deseado
En el checkout:
✅ Domain Registration
✅ Domain Privacy (gratis)
❌ PremiumDNS (no necesario)
❌ Hosting (usaremos EC2)
2. Crear instancia EC2
2.1 Configuración

Collapse
Save
Copy
1
AWS Console → EC2 → Launch Instance
Name: nombre-proyecto
AMI: Ubuntu Server 22.04/26.04 LTS (Free tier eligible)
Instance type: t2.micro o t3.micro (Free tier eligible)
Storage: 20 GiB gp3
2.2 Key Pair
Crear nuevo key pair
Type: RSA
Format: .pem
⚠️ Guardar el archivo .pem en un lugar seguro, no se puede recuperar
2.3 Security Group
✅ Allow SSH (port 22)
✅ Allow HTTP (port 80)
✅ Allow HTTPS (port 443)
3. Elastic IP (IP fija)

Collapse
Save
Copy
1
EC2 → Network & Security → Elastic IPs → Allocate
Luego asociarla a la instancia:


Collapse
Save
Copy
1
Actions → Associate Elastic IP → seleccionar instancia → Associate
⚠️ Apunta la IP, la necesitarás para el dominio y el SSH.

4. Conectarse al servidor
bash

Collapse
Save
Copy
1
2
3
4
5
# Dar permisos al archivo .pem
chmod 400 ~/ruta/a/tu-clave.pem

# Conectarse
ssh -i ~/ruta/a/tu-clave.pem ubuntu@TU_ELASTIC_IP
5. Preparar el servidor
bash

Collapse
Save
Copy
1
2
3
4
5
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias
sudo apt install python3-pip python3-venv nginx git -y
6. Subir el proyecto
bash

Collapse
Save
Copy
1
2
3
cd ~
git clone https://github.com/tu-usuario/crochet-shop.git
cd crochet-shop
7. Entorno virtual y dependencias
bash

Collapse
Save
Copy
1
2
3
4
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
8. Variables de entorno
bash

Collapse
Save
Copy
1
nano /home/ubuntu/crochet-shop/.env
env

Collapse
Save
Copy
1
2
3
4
5
6
7
8
9
SECRET_KEY=una-clave-secreta-larga-y-random
DEBUG=False
ALLOWED_HOSTS=tudominio.com,www.tudominio.com,TU_ELASTIC_IP

# S3
AWS_ACCESS_KEY_ID=tu-access-key
AWS_SECRET_ACCESS_KEY=tu-secret-key
AWS_STORAGE_BUCKET_NAME=nombre-bucket
AWS_S3_REGION_NAME=eu-north-1
Generar SECRET_KEY:

bash

Collapse
Save
Copy
1
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
9. Migraciones y archivos estáticos
bash

Collapse
Save
Copy
1
2
python manage.py migrate
python manage.py collectstatic
10. Configurar Gunicorn
bash

Collapse
Save
Copy
1
sudo nano /etc/systemd/system/gunicorn.service
ini

Collapse
Save
Copy
1
2
3
4
5
6
7
8
9
10
11
12
13
14
[Unit]
Description=Gunicorn Django - crochet-shop
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/crochet-shop
ExecStart=/home/ubuntu/crochet-shop/venv/bin/gunicorn \
          --workers 3 \
          --bind unix:/home/ubuntu/crochet-shop/gunicorn.sock \
          crochet_shop.wsgi:application

[Install]
WantedBy=multi-user.target
bash

Collapse
Save
Copy
1
2
3
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
sudo systemctl status gunicorn
11. Configurar Nginx
bash

Collapse
Save
Copy
1
sudo nano /etc/nginx/sites-available/crochet-shop
nginx

Collapse
Save
Copy
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
server {
    listen 80;
    server_name tudominio.com www.tudominio.com;

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        root /home/ubuntu/crochet-shop;
    }

    location /media/ {
        root /home/ubuntu/crochet-shop;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/ubuntu/crochet-shop/gunicorn.sock;
    }
}
bash

Collapse
Save
Copy
1
2
3
4
5
6
7
8
# Activar el sitio
sudo ln -s /etc/nginx/sites-available/crochet-shop /etc/nginx/sites-enabled

# Verificar configuración
sudo nginx -t

# Reiniciar
sudo systemctl restart nginx
Permisos del socket
bash

Collapse
Save
Copy
1
2
sudo chmod 755 /home/ubuntu
sudo chmod 755 /home/ubuntu/crochet-shop
12. Apuntar dominio a EC2 (Namecheap)

Collapse
Save
Copy
1
Namecheap → Domain List → Manage → Advanced DNS
Eliminar registros existentes y añadir:

TYPE
HOST
VALUE
TTL
A Record
@
TU_ELASTIC_IP
30 min
A Record
www
TU_ELASTIC_IP
30 min


⏳ Esperar entre 5 minutos y 1 hora para la propagación DNS.

13. SSL con Certbot
bash

Collapse
Save
Copy
1
2
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d tudominio.com -d www.tudominio.com
14. Configurar S3 para media files
14.1 Crear bucket S3

Collapse
Save
Copy
1
2
3
4
AWS Console → S3 → Create bucket
- Nombre: nombre-proyecto-media
- Región: eu-north-1
- Desmarcar "Block all public access"
14.2 Bucket policy

Collapse
Save
Copy
1
S3 → bucket → Permissions → Bucket policy
json

Collapse
Save
Copy
1
2
3
4
5
6
7
8
9
10
11
12
⌄
⌄
⌄
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::nombre-bucket/*"
        }
    ]
}
14.3 Crear usuario IAM

Collapse
Save
Copy
1
2
3
IAM → Users → Create user
- Username: nombre-proyecto-s3
- Permissions: AmazonS3FullAccess
Luego crear Access Key:


Collapse
Save
Copy
1
2
Usuario → Security credentials → Access keys → Create access key
- Use case: Application running on AWS compute service
⚠️ Guardar Access Key ID y Secret Access Key.

15. Script de deploy
bash

Collapse
Save
Copy
1
nano ~/deploy.sh
bash

Collapse
Save
Copy
1
2
3
4
5
6
7
8
#!/bin/bash
cd ~/crochet-shop
source venv/bin/activate
git pull
python manage.py migrate
python manage.py collectstatic --no-input
sudo systemctl restart gunicorn
echo "✅ Deploy completado!"
bash

Collapse
Save
Copy
1
chmod +x ~/deploy.sh
Ejecutar cada vez que hagas cambios:

bash

Collapse
Save
Copy
1
bash deploy.sh
16. Flujo de trabajo diario
bash

Collapse
Save
Copy
1
2
3
4
5
6
7
# 1. En local: hacer cambios y subir
git add .
git commit -m "descripción del cambio"
git push origin main

# 2. En el servidor: actualizar
bash deploy.sh
🔧 Comandos útiles
bash

Collapse
Save
Copy
1
2
3
4
5
6
7
8
9
10
11
12
13
# Ver logs de Gunicorn
sudo journalctl -u gunicorn --no-pager -n 50

# Ver logs de Nginx
sudo tail -f /var/log/nginx/error.log

# Reiniciar servicios
sudo systemctl restart gunicorn
sudo systemctl restart nginx

# Estado de servicios
sudo systemctl status gunicorn
sudo systemctl status nginx
⚠️ Cosas importantes
El archivo .pem no se puede recuperar, guárdalo bien
El .env nunca debe subirse a git, añadirlo al .gitignore
La carpeta staticfiles/ y media/ tampoco deben ir en git
La Elastic IP es gratis mientras esté asociada a una instancia activa
El certificado SSL se renueva automáticamente cada 90 días