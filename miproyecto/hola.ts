// Definimos una interfaz para un usuario
interface Usuario {
  id: number;
  nombre: string;
  correo: string;
  activo: boolean;
}

// Función que recibe un usuario y devuelve un saludo
function saludar(usuario: Usuario): string {
  return `Hola, ${usuario.nombre}! Tu correo es ${usuario.correo}`;
}

// Clase que maneja una lista de usuarios
class GestorUsuarios {
  private usuarios: Usuario[] = [];

  agregarUsuario(usuario: Usuario): void {
    this.usuarios.push(usuario);
  }

  listarUsuarios(): void {
    this.usuarios.forEach((u) => {
      console.log(saludar(u));
    });
  }
}

// Crear instancia y usar la clase
const gestor = new GestorUsuarios();

gestor.agregarUsuario({
  id: 1,
  nombre: 'Ana',
  correo: 'ana@example.com',
  activo: true,
});

gestor.agregarUsuario({
  id: 2,
  nombre: 'Luis',
  correo: 'luis@example.com',
  activo: false,
});

// Listar usuarios
gestor.listarUsuarios();
