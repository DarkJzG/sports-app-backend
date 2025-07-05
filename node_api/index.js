const express = require('express');
const cors = require('cors');
const app = express();

app.use(cors());
app.use(express.json());

app.get('/api/test', (req, res) => {
  res.json({ message: 'Node funcionando correctamente' });
});

app.listen(4000, () => {
  console.log('Servidor Node.js en puerto 4000');
});