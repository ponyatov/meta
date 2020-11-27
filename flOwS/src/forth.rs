type Command = fn(); // -> ();

struct WORD {
    _cfa: &'static Command,
    _immed: bool,
}

// #[macro_use]
// extern crate lazy_static;
use lazy_static::lazy_static;
use std::sync::Mutex;

lazy_static! {
    static ref S: Mutex<Vec<i32>> = Mutex::new({
        let m = Vec::new();
        m
    });
}

use std::collections::HashMap;

// global vocabulary
lazy_static! {
    static ref W: Mutex<HashMap<&'static str, WORD>> = Mutex::new({
        let mut m = HashMap::new();
        m.insert("NOP",WORD::new(nop));
        m
    });
}

fn nop(){}

// bytecode opcodes
lazy_static! {
    static ref OP: HashMap<&'static str, u8> = {
        let mut m = HashMap::new();
        m.insert("nop", 0x00);
        m.insert("bye", 0xFF);
        m
    };
}

// FORTH shell entry point
pub fn forth() {
    println!("FORTH");
    println!("nop: {}", OP.get(&"nop").unwrap());
    // println!("jmp: {}", OP.get(&"jmp").unwrap());
    println!("bye: {}", OP.get(&"bye").unwrap());
    interpret();
}

// REPL
fn interpret() {
    // loop {
    bl();
    q();
    key();
    emit();
    // }
}

// ( -- key ) get next char from stdin
fn key() {
    let _input = std::io::stdin();
}

// ( char -- ) put char to stdout
fn emit() {
    println!("{:?}", S.lock().unwrap().pop().unwrap());
}

// ( -- bl ) push [space] char
fn bl() {
    S.lock().unwrap().push(0x20); // space
}

// ( -- ) print data stack
fn q() {
    // println!("stack: {:?}", stack);
}
