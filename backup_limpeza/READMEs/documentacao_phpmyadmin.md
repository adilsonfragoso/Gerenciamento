## Documentação de Configuração do MySQL e phpMyAdmin em Docker Swarm

Esta documentação resume todo o processo de configuração realizado, incluindo:

* Deploy de stack com MySQL e phpMyAdmin
* Restrição de acesso do root a IPs específicos
* Criação de usuário dedicado ao phpMyAdmin
* Regras de firewall para acesso remoto
* Testes de conexão em diferentes ambientes

---

### 1. Remoção da Stack Antiga

1. No Portainer → **Stacks** → selecione a stack antiga → **Remove**
2. Marcar **Remove volumes** para limpar o volume `mysql_data` antigo

### 2. Criar Config com Script de Inicialização

No Portainer → **Configs** → **Add config**:

* **Name**: `restrict_root_sql`
* **Content** (10\_restrict\_root.sql):

```sql
-- usuario root@localhost
CREATE OR REPLACE USER 'root'@'localhost' IDENTIFIED BY 'Define@4536#8521';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' WITH GRANT OPTION;

-- root via TCP local
CREATE OR REPLACE USER 'root'@'127.0.0.1' IDENTIFIED BY 'Define@4536#8521';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'127.0.0.1' WITH GRANT OPTION;

-- root para seu PC
CREATE OR REPLACE USER 'root'@'201.27.236.6' IDENTIFIED BY 'Define@4536#8521';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'201.27.236.6' WITH GRANT OPTION;

-- root para outra VPS
CREATE OR REPLACE USER 'root'@'145.223.29.250' IDENTIFIED BY 'Define@4536#8521';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'145.223.29.250' WITH GRANT OPTION;

-- remover wildcard
DROP USER IF EXISTS 'root'@'%';
FLUSH PRIVILEGES;
```

### 3. Deploy da Nova Stack

Portainer → **Stacks** → **Add stack** → cole o `stack.yml`:

```yaml
version: "3.7"

configs:
  restrict_root_sql:
    external: true

services:
  mysql:
    image: mysql:8.0
    command:
      [
        --character-set-server=utf8mb4,
        --collation-server=utf8mb4_general_ci,
        --default-authentication-plugin=mysql_native_password
      ]
    environment:
      MYSQL_ROOT_PASSWORD: Define@4536#8521
    volumes:
      - mysql_data:/var/lib/mysql
      - /etc/localtime:/etc/localtime:ro
    networks:
      - system_network
    configs:
      - source: restrict_root_sql
        target: /docker-entrypoint-initdb.d/10_restrict_root.sql
    ports:
      - target: 3306
        published: 3306
        protocol: tcp
        mode: host
    deploy:
      mode: replicated
      replicas: 1
      placement:
        constraints: [node.role == manager]
      resources:
        limits:
          cpus: "1"
          memory: 2048M

  phpmyadmin:
    image: phpmyadmin/phpmyadmin:latest
    command: ["apache2-foreground"]
    environment:
      - PMA_HOSTS=mysql
      - PMA_PORT=3306
      - PMA_ABSOLUTE_URI=https://pma.linksystems.com.br
      - UPLOAD_LIMIT=256M
    networks:
      - system_network
    deploy:
      mode: replicated
      replicas: 1
      placement:
        constraints: [node.role == manager]
      resources:
        limits:
          cpus: "2"
          memory: 2048M
      labels:
        - traefik.enable=true
        - traefik.http.routers.phpmyadmin.rule=Host(`pma.linksystems.com.br`)
        - traefik.http.routers.phpmyadmin.entrypoints=web,websecure
        - traefik.http.routers.phpmyadmin.tls.certresolver=letsencryptresolver
        - traefik.http.services.phpmyadmin.loadbalancer.server.port=80
        - traefik.http.routers.phpmyadmin.service=phpmyadmin

networks:
  system_network:
    external: true
    name: system_network

volumes:
  mysql_data:
```

Clique **Deploy the stack** e aguarde **mysql** e **phpmyadmin** ficarem `Running`.

### 4. Verificação de Execução do Script

Portainer → **Services** → **mysql** → **Logs** → deve conter:

```
running /docker-entrypoint-initdb.d/10_restrict_root.sql
```

### 5. Firewall da VPS

```bash
ufw allow from 201.27.236.6 to any port 3306 proto tcp
ufw allow from 145.223.29.250 to any port 3306 proto tcp
ufw deny 3306/tcp
ufw reload
```

### 6. Criação de Usuário phpMyAdmin Personalizado

Identificação de IP interno do phpMyAdmin: **10.0.1.4**

No MySQL:

```sql
CREATE USER 'adseg'@'10.0.1.%' IDENTIFIED BY 'Define@4536#8521';
GRANT ALL PRIVILEGES ON *.* TO 'adseg'@'10.0.1.%' WITH GRANT OPTION;
DROP USER IF EXISTS 'admin'@'10.0.1.%';
FLUSH PRIVILEGES;
```

Fazer login em `https://pma.linksystems.com.br` com **adseg/Define\@4536#8521**.

### 7. Testes de Conexão

* **Local no host**:

  * `docker exec -it <ID_MYSQL> mysql -h127.0.0.1 -uroot -p` ou `mysql -uroot -p`
* **PC remoto (201.27.236.6)** e **VPS externa (145.223.29.250)**:

  * `mysql -h<IP_VPS> -P3306 -uroot -p`
* **Windows**:

  * Usar MySQL Shell:

    ```
    mysqlsh> \sql
    MySQL SQL> \connect root@147.93.8.196:3306 <Define@4536#8521>
    ```
  * Ou instalar MySQL Client e rodar:

    ```powershell
    mysql -h147.93.8.196 -P3306 -uroot -p"Define@4536#8521"
    ```

---

**Resultado Final**

* MySQL na Stack Swarm com dados persistidos.
* Acesso `root` restrito a `localhost`, `127.0.0.1`, `201.27.236.6`, `145.223.29.250`.
* phpMyAdmin acessível via `adseg@10.0.1.%`.<
* Firewall bloqueando acesso de IPs não autorizados.
* Conexões de clientes Windows, Linux e scripts Python devidamente testadas.
