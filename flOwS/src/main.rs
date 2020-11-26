// \ <section:top>
use std::env;
mod hello;
mod forth;
// / <section:top>
// \ <section:bot>
fn main() {
    //
    let argv: Vec<String> = env::args().collect();
    let argc = argv.len();
    for i in 0..argc { println!("argv[{}] = {:?}",i,argv[i]); }
    //
    hello::hello();
    forth::forth();
}
// / <section:bot>
