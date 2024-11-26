import ollama
desiredModel='llama3.2:1b'
questionToAsk1='What is the best strategy to learn coding?'

llama = ollama.chat(model=desiredModel, messages=[
  {'role': 'user',
    'content': questionToAsk1,},])

response1=llama['message']['content']

htmlText = '<div class="css-1ebprri"><h3 class="chakra-text css-147tqph" data-testid="viewJobDetailsSectionTitle">Full Job Description</h3><div class="css-0"><div><div data-skipa11y="true" data-testid="viewJobBodyJobFullDescriptionContent" class="css-cxpe4v"><p><b>Overview</b><br>We are looking for an experienced and talented Senior Front-End Developer to join our team at Storagely. In this role, you will be responsible for designing and implementing highly responsive and visually stunning user interfaces for our core web application. You will lead front-end development efforts, set best practices, and work closely with product managers, designers, back-end developers and our CTO to deliver an exceptional user experience.</p><p><b>Duties</b></p><ul><li>Lead the development and implementation of front-end architecture and UI components.</li><li>Collaborate with design and product teams to translate wireframes, mockups, and prototypes into responsive and interactive user interfaces.</li><li>Write clean, maintainable, and scalable code using modern front-end technologies.</li><li>Optimize web applications for performance, speed, and scalability.</li><li>Mentor and guide junior developers, conducting code reviews to ensure quality and adherence to best practices.</li><li>Stay updated on emerging technologies and industry trends, evaluating and integrating them into the development process when appropriate.</li><li>Work with back-end developers to ensure seamless integration of APIs and data.</li><li>Troubleshoot, debug, and resolve issues across different devices and browsers.</li><li>Integrate new technologies such as AI response streaming and 3rd party SDKs.</li></ul><p><b>Experience</b></p><ul><li>5+ years of professional experience in front-end development.</li><li>Expertise in modern JavaScript frameworks such as React, Vue.js, or Angular.</li><li>Proficiency in HTML, CSS, and preprocessors like SASS or LESS.</li><li>Strong understanding of responsive design principles and cross-browser compatibility.</li><li>Experience with state management libraries like Redux, Vuex, or similar.</li><li>Proficiency in build tools and bundlers like Webpack, Vite, or Parcel.</li><li>Deep knowledge of web performance optimization techniques.</li><li>Experience with version control systems, such as Git, and CI/CD workflows.</li><li>Familiarity with back-end integration, RESTful APIs, and GraphQL.</li><li>Strong problem-solving skills and attention to detail.</li><li>Excellent communication and collaboration skills.</li><li>Understanding of web application security best practices.</li><li>Ability to work independently and collaboratively in a team environment.</li></ul><p>Job Type: Full-time</p><p>Pay: $70,000.00 - $100,000.00 per year</p><p>Benefits:</p><ul><li>401(k)</li><li>401(k) matching</li><li>Dental insurance</li><li>Flexible schedule</li><li>Flexible spending account</li><li>Health insurance</li><li>Life insurance</li><li>Paid time off</li><li>Vision insurance</li></ul><p>Schedule:</p><ul><li>8 hour shift</li><li>Choose your own hours</li><li>Monday to Friday</li><li>No weekends</li></ul><p>Work Location: Remote</p></div></div></div></div>'

questionToAsk2='from the following text which are programming languages: ' + htmlText

llama = ollama.chat(model=desiredModel, messages=[
  {'role': 'user',
    'content': questionToAsk2,},])

response2=llama['message']['content']

print(response1)
print("-----------------------------------")
print(response2)

