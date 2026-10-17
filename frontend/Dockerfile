FROM node:20-alpine
WORKDIR /app
COPY package.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 3000
ENV NEXT_PUBLIC_API_BASE=http://localhost:8000
CMD ["npm", "start"]
