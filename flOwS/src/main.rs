// \ <section:top>
use std::env;
mod hello;
mod forth;
// / <section:top>
// \ <section:bot>
fn main() {
    let argv = env::args_os();
    let argc = argv.len();
    println!("argc:[{:?}] argv:[{:?}]",argc,argv);
    hello::hello();
    forth::forth();
}
// / <section:bot>
