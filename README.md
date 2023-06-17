# BOSCH CODERACE CHALLENGE 2023 ROUND 4
## Topic: Data Migration
Team name: **OnePlusTwo**

Members:
- Hoang Nghia Viet
- Mai Chien Vi Thien
- Bui Nguyen Hoang

## Installation
1. Install Docker [here](https://www.docker.com/products/docker-desktop/)
2. Clone the repository 
```shell!
git clone https://github.com/hoangnghiaviet/Bosch-CodeRace-Round4.git
```

## Run task
### Task 1
1. Run `pip install -r requirements.txt` to intall necessary packages. 
1. Set the values of **TOKEN**, **BRANCH_NAME**, and **REPOSITORY_NAME** in the **secret.env** file to update the GitHub repository information of the user for **task1** and **task2**.
2. In the previous Upload Rst file task, we allow users to choose the location to upload the **ECU_Requirement.rst** file and update the path and caption in the **UploadFileRst** sheet of the **config.xlsx** file.
3. Run `python task1.py` to update **index.rst** according to **config.xlsx** and push result to GitHub.

### Task2
1. Execute the command `python task2.py` to upload the pipeline **build_docs.yml** to the **.github/workflows/** folder in the repository. This will enable the GitHub action to execute the workflow and deploy the HTML to the GitHub Pages.

### Task 3
1. To set up Airflow, in folder **task3/dags/input/**:
* Set the values of **TOKEN**, **BRANCH_NAME**, and **REPOSITORY_NAME** in the **secret.env** file to update the GitHub repository information of the user for **task3**.
* Update your **Requirements.reqif** file.
* To customize the output in **JSON** and **RST** files, please refer to the **UserGuide** sheet in the **config.xlsx** file and configure the necessary values accordingly.

2. All of the following command lines are executed within the **task3** folder.

* Init airflow on your local
```shell!
docker compose up airflow-init
```

* Install necessary packages
```shell!
docker build . --tag apache/airflow:2.6.1
```

* Run the command to deploy the Apache Airflow web server, and allow a few minutes for the server to go live.
```shell!
docker compose up -d
```

3. Access to **localhost:8080** and login using the following account: 
> username: airflow
> password: airflow

<img src="https://scontent.fsgn2-6.fna.fbcdn.net/v/t1.15752-9/353358059_656144683036152_1964817078754583608_n.png?_nc_cat=111&ccb=1-7&_nc_sid=ae9488&_nc_ohc=uNV3n8Ci32kAX8fxebf&_nc_oc=AQl6mKKQcP8WKGz--193OKOwIETLmeCHj3m2uP-AS4vPwQxnR3yhJD_3rd3LsInZT68&_nc_ht=scontent.fsgn2-6.fna&oh=03_AdQnZ4Fxrn0cUBii4C3xF-cb5a_kt7CuAbitmt1JwrDxYw&oe=64B3B3D4" width="90%">

4. Go to **DAG: oneplustwo_work_flow**, click **Trigger DAG** to run the work flow
<img src="https://scontent.fsgn2-3.fna.fbcdn.net/v/t1.15752-9/354533245_185616420833025_1197806746650175012_n.png?_nc_cat=107&ccb=1-7&_nc_sid=ae9488&_nc_ohc=lgFlLZVLoLMAX-Byg9A&_nc_ht=scontent.fsgn2-3.fna&oh=03_AdTrWA0POgu81vw6yPIpsGcf9LUNlrzZo6oj4ehDM9QKUw&oe=64B398B0" width="90%">
<img src="https://scontent.fsgn2-4.fna.fbcdn.net/v/t1.15752-9/354779079_1100257744281773_5273605504311809827_n.png?_nc_cat=101&ccb=1-7&_nc_sid=ae9488&_nc_ohc=uR4jaPLz8bMAX9zya80&_nc_ht=scontent.fsgn2-4.fna&oh=03_AdQ4Ut0KxW-QemN1GlYkbeNVsbv7R14DG17Fg_wsXOsqfQ&oe=64B3B75C" width="90%">

5. The graph of work flow
<img src="https://scontent.fsgn2-9.fna.fbcdn.net/v/t1.15752-9/354771896_6621605424538552_6069997185191957695_n.png?_nc_cat=105&ccb=1-7&_nc_sid=ae9488&_nc_ohc=UYgmCw-kiuIAX89CEtZ&_nc_ht=scontent.fsgn2-9.fna&oh=03_AdTbSYVYsDzPpj7cWaMCThkaqxUm-GhMFIXUpsi7c3JYCQ&oe=64B3BE95" width="90%">