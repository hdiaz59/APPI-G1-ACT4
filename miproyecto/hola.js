// Función que recibe un usuario y devuelve un saludo
function saludar(usuario) {
    return "Hola, ".concat(usuario.nombre, "! Tu correo es ").concat(usuario.correo);
}
// Clase que maneja una lista de usuarios
var GestorUsuarios = /** @class */ (function () {
    function GestorUsuarios() {
        this.usuarios = [];
    }
    GestorUsuarios.prototype.agregarUsuario = function (usuario) {
        this.usuarios.push(usuario);
    };
    GestorUsuarios.prototype.listarUsuarios = function () {
        this.usuarios.forEach(function (u) {
            console.log(saludar(u));
        });
    };
    return GestorUsuarios;
}());
// Crear instancia y usar la clase
var gestor = new GestorUsuarios();
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
