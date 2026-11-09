# Slika za frontend: Node.js z nameščenimi knjižnicami iz package-lock.json
FROM node:24-alpine

WORKDIR /app

# Najprej samo package*.json, da Docker knjižnic ne nameša ob vsaki spremembi kode
COPY package.json package-lock.json ./
RUN npm ci

COPY . .

EXPOSE 5173

# --host 0.0.0.0 pomeni, da je Vite dosegljiv tudi izven vsebnika
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
