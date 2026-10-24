"use strict";

const fs = require("node:fs");

const NUMERO = /^[+-]?(?:[0-9]+(?:\.[0-9]+)?|\.[0-9]+)$/;

function escribir(...valores) {
  // fs.writeSync conserva el orden de Escribir y muestra el prompt antes de Leer.
  fs.writeSync(1, valores.join("") + "\n");
}

function leerLinea() {
  // Lee una línea por byte: funciona con consola interactiva y stdin enviado en lote.
  const bytes = [];
  const byte = Buffer.alloc(1);
  while (true) {
    const cantidad = fs.readSync(0, byte, 0, 1, null);
    if (cantidad === 0) {
      if (bytes.length === 0) throw new Error("No hay más datos de entrada.");
      break;
    }
    if (byte[0] === 10) break;
    if (byte[0] !== 13) bytes.push(byte[0]);
  }
  return Buffer.from(bytes).toString("utf8");
}

function leerNumero() {
  // Valida la misma forma decimal y finitud usada por el runtime del compilador.
  const entrada = leerLinea().trim();
  if (!NUMERO.test(entrada)) throw new Error("Se esperaba un número decimal finito.");
  const valor = Number(entrada);
  if (!Number.isFinite(valor)) throw new Error("Se esperaba un número decimal finito.");
  return valor;
}

function numeroATexto(valor) {
  // JavaScript y el helper del compilador omiten el sufijo .0 de enteros.
  if (Number.isInteger(valor)) return String(valor);
  return String(Number(valor.toPrecision(15)));
}

// Cada Escribir termina la línea antes de la lectura correspondiente.
escribir("Ingrese el primer número:");
const a = leerNumero();
escribir("Ingrese el segundo número:");
const b = leerNumero();
escribir("Ingrese el tercer número:");
const c = leerNumero();

// Los paréntesis preservan la agrupación del programa A.
const resultado = ((a + b) * c) - (a / b);

// Se concatena sin agregar un espacio entre los argumentos.
escribir("El resultado es: ", numeroATexto(resultado));
