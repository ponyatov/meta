// \ <section:top>
use std::env;
mod hello;
mod forth;
// / <section:top>
// \ <section:bot>
fn main() {
    println!("args: {:?}",env::args_os());
    hello::hello();
    forth::forth();
}
// / <section:bot>
