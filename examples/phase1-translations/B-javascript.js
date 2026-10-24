"use strict";

const fs = require("node:fs");

const NUMERO = /^[+-]?(?:[0-9]+(?:\.[0-9]+)?|\.[0-9]+)$/;

function escribir(...valores) {
  // La escritura síncrona evita que la lectura bloqueante esconda el prompt.
  fs.writeSync(1, valores.join("") + "\n");
}

function leerLinea() {
  // Consume una línea; las demás entradas quedan disponibles para la siguiente lectura.
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
  // Number acepta más formatos; la expresión mantiene la sintaxis del compilador.
  const entrada = leerLinea().trim();
  if (!NUMERO.test(entrada)) throw new Error("Se esperaba un número decimal finito.");
  const valor = Number(entrada);
  if (!Number.isFinite(valor)) throw new Error("Se esperaba un número decimal finito.");
  return valor;
}

// Los mensajes de Escribir se conservan antes de leer sus valores.
escribir("Ingrese su nota final:");
const nota = leerNumero();
escribir("Ingrese su porcentaje de asistencia:");
const asistencia = leerNumero();

// Se mantienen el mayor o igual y la estructura de Si/Sino anidada.
if (nota >= 6 && asistencia >= 75) {
  escribir("Aprobado");
} else {
  if (nota >= 6 && asistencia < 75) {
    escribir("Reprobado por asistencia");
  } else {
    escribir("Reprobado por nota");
  }
}
