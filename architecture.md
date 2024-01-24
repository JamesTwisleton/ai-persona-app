# TODO: move this to documentation folder as part of dockerisation PR

# Architecture

## 1. Introduction
The purpose of this document is to outline the architectural design for an AI persona web application that involves integration with various technologies, including:
* Next.js
* Docker for containerisation
* GitHub Actions for CI/CD
* ECR for container hosting
* ECS for service deployment
* MongoDB for data persistence
* S3 for image storage
* OpenAI's DALL-E API for persona image generation
* [Replicate API's OpenJourney model](https://replicate.com/prompthero/openjourney) for persona image generation
* OpenAI's ChatGPT API for motto generation

The application's primary functionality is to process a user request to generate an artificial social media persona (image and phrase).

## 2. System Architecture
<img src="architecture.png" alt="scheme" width="800"/>


### 2.1 Frontend (Next.js)
The frontend is built using Next.js. It will handle user input, send requests to the backend, and display generated content.

### 2.2 Backend (Next.js)
The backend is built uing Next.js. It is responsible for coordinating the workflow between the frontend, OpenAI, Replicate, AWS and MongoDB.

#### 2.2.1 Communication with MongoDB
The backend connects to MongoDB to store and retrieve data about personas

#### 2.2.2 Communication with Replicate / DALL-E

The backend communicates with Replicate API's OpenJourney model or OpenAI's DALL-E API to generate an image persona based on user input (persona name & descriptive prompt). After sending a request, a generated image URL is returned.

#### 2.2.3 Communication with ChatGPT
The backend communicates with OpenAI's ChatGPT  API using the original descriptive prompt input for image generation, as well as a categorial "motto tone", which acts as a personality flavor to help ChatGPT generate a suitable motto. In response, ChatGPT generates a personalised phrase which is linked back to the generated persona.

### 2.3 Persona Generation Workflow
1. **Frontend Request**: User input consisting of name, descriptive prompt and motto-tone is sent from the frontend to the backend.

2. **Communication with MongoDB**: The backend checks MongoDB to see if there is an existing persona associated with the provided persona name.

3. **Communication with Replicate / DALL-E**: If the persona name does not have a MongoDB entry, the backend sends a request to OpenJourney or DALL-E to create a new image for the provided person name and description. An image URL for the generated persona image is generated.

5. **Download Image**: The backend downloads the image from the generated image URL.

6. **Upload to S3**: The downloaded image is then uploaded to an S3 bucket, and a unique S3 bucket address is generated.

7. **Upsert to MongoDB**: If there is not already a persona for the user provided name, a new persona entry is created, including the new image and attributes (name, motto_tone, descriptive, prompt). If a persona for the user provided name already exists, a new image is added to the persona's mongo entry.

8. **Retrieving pre-existing personas from MongoDB**: On request, MongoDB grabs all the s3 bucket addresses for the images associated with a provided persona. AWS then generates short lived image URLs (60 seconds) which are provided to the frontend along with the other metadata.

## 3. Technology Stack

- **Frontend/Backend:** Next.js
- **Database:** MongoDB
- **Image Generation:** OpenAI DALL-E and Replicate's OpenJourney model
- **Motto Generation:** OpenAI ChatGPT
- **Storage:** S3

## 4. Infrastructure as Code (IaC)

Infrastructure is managed using Terraform. The Terraform scripts define the AWS resources, including S3 buckets and any necessary IAM roles.

## 5. Security Considerations

Ensure secure communication between components using HTTPS. Implement proper access controls and authentication mechanisms for MongoDB and Amazon S3. Protect API keys and credentials using environment variables. In the future, user authentication will be added.

## 6. Conclusion

This architectural design provides a high-level overview of the web application's components, their interactions, and the technologies used. It is crucial to follow best practices for security and scalability while implementing and deploying this system. Regular monitoring and maintenance should be performed to ensure optimal performance and reliability.

## 6. Contributors

[JamesTwisleton](https://github.com/JamesTwisleton)

[Sum02dean](https://github.com/sum02dean)
