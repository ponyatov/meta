pub fn forth() {
    println!("FORTH");
    interpret();
}

// #[macro_use]
// extern crate lazy_static;
use lazy_static::lazy_static;

lazy_static! {
    static ref S: Vec<i32> = vec![];
}

use std::collections::HashMap;

lazy_static! {
    static ref W: HashMap<&'static str, u32> = {
        let mut voc = HashMap::new();
        voc.insert("nop", 0);
        voc
    };
}

fn interpret() {
    // loop {
    bl();
    q();
    key();
    emit();
    // }
}

fn key() {
    let _input = std::io::stdin();
}

fn emit() {
    println!("{:?}", S.pop());
}

fn bl() {
    S.push(0x20); // space
}

fn q() {
    // println!("stack: {:?}", stack);
}
