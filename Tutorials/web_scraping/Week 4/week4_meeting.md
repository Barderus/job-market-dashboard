## Meeting overview

- We discussed how we are going to structure our dataframes
  - Example:
| unique_title | title  | job_location | education | languages  | framework   | others   | wage | salary | company   | remote | job_type     |
|--------------|--------|--------------|-----------|------------|-------------|----------|------|--------|-----------|--------|--------------|
|              |        |              |           |            |             |          |      |        |           |        |              |
|              |        |              |           |            |             |          |      |        |           |        |              |
|              |        |              |           |            |             |          |      |        |           |        |              |


### Column Labels Explanation:
* **unique_title:** A unique identifier for each job title, ensuring no duplicates.
* **title:** The official job title or position name.
* **job_location:** The physical or primary location of the job, such as city or region.
* **education:ollama run llama3.2** The educational qualifications required, such as degree or certifications.
* **languages:** Programming languages needed for the position.
* **framework:** Relevant development frameworks or libraries required, e.g., Django, React.
* **others:** Any additional skills or tools necessary for the job, e.g., Git, DevOps.
* **wage:** The hourly rate or wage offered for the job.
* **salary:** The annual salary offered for the position.
* **company:** The name of the company offering the job.
* **remote:** Specifies if the job is remote, in-person or hybrid.
* **job_type:** The type of job, such as full-time, part-time, contract, or internship.


- **For next week**: I will search the advantages of using Llama for data analysis on the collected scraped data. (Anyone is free to search it up as well)
  - **If Viable**: We can consider scraping data from any of the following job sites:
    - Indeed
    - ZipRecruiter
    - Glassdoor
    - LinkedIn
    - SimplyHired
    - Monster
    - JobList
    - USAJobs
  - **If Not Viable**: These sites have structured HTML elements (classes and IDs) that could help us in the data scrapping:
    - Glassdoor (possibly)
    - SimplyHired
    - Monster
    - JobList
  - **For Long-Text Pages**: We could use list comprehensions and split data based on keywords like "Job Qualifications" to get the important information.
