* {

  margin: 0;

  padding: 0;

  box-sizing: border-box;

}



body {

  font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;

  background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);

  min-height: 100vh;

}



.admin-container {

  max-width: 1400px;

  margin: 0 auto;

  padding: 20px;

}



.header {

  background: white;

  padding: 30px;

  border-radius: 15px;

  margin-bottom: 30px;

  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);

  display: flex;

  justify-content: space-between;

  align-items: center;

}



.header h1 {

  color: #333;

  font-size: 2em;

}



.user-info span {

  color: #666;

  font-size: 1.1em;

}



.dashboard {

  margin-bottom: 30px;

}



.stats-grid {

  display: grid;

  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));

  gap: 20px;

  margin-bottom: 30px;

}



.stat-card {

  background: white;

  padding: 30px;

  border-radius: 15px;

  text-align: center;

  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);

}



.stat-number {

  font-size: 3em;

  font-weight: bold;

  color: #2c3e50;

  margin-bottom: 10px;

}



.stat-label {

  color: #666;

  font-size: 1em;

}



.card {

  background: white;

  padding: 30px;

  border-radius: 15px;

  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);

  margin-bottom: 30px;

}



.card h3 {

  color: #333;

  margin-bottom: 20px;

  font-size: 1.3em;

}



.table-container {

  overflow-x: auto;

  margin-bottom: 20px;

}



table {

  width: 100%;

  border-collapse: collapse;

}



th,

td {

  padding: 12px;

  text-align: left;

  border-bottom: 1px solid #ddd;

}



th {

  background: #f8f9fa;

  font-weight: 600;

  color: #333;

}



tr:hover {

  background: #f8f9fa;

}



.btn-refresh {

  background: #28a745;

  color: white;

  border: none;

  padding: 10px 20px;

  border-radius: 8px;

  cursor: pointer;

}



.admin-actions {

  display: grid;

  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));

  gap: 15px;

}



.btn-action {

  background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);

  color: white;

  border: none;

  padding: 15px;

  border-radius: 8px;

  cursor: pointer;

  font-size: 16px;

  transition: transform 0.2s;

}



.btn-action:hover {

  transform: translateY(-2px);

}



.footer {

  text-align: center;

}



.btn-logout {

  background: #dc3545;

  color: white;

  border: none;

  padding: 12px 30px;

  border-radius: 8px;

  cursor: pointer;

  font-size: 16px;

}



.btn-logout:hover {

  background: #c82333;

}
