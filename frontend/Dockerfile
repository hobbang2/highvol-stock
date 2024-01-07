# Setting base image
FROM node:18-alpine as build

# Setting working directory for container
WORKDIR /app

# Copy dependencies
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy file from host machine to container
COPY . .

# npm build
RUN npm run build

FROM nginx:stable-alpine

# Copy build result to /usr/share/nginx/html
COPY --from=build /app/build /usr/share/nginx/html

# Delete basic setting file to prevent conflict with custom setting 
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom setting file to container
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

# Run nginx server on background
CMD ["nginx", "-g", "daemon off;"]
