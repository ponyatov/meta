enum Option<T> {
    Some(T),
    None,
}

use std::fmt;

impl std::fmt::Display for Option<f32> {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            Option::Some(x) => write!(f, "{}", x),
            Option::None => write!(f, "<none>"),
        }
    }
}

fn inc(x: f32) -> Option<f32> {
    if x > 0. {
        Option::Some(x + 1.)
    } else {
        Option::None
    }
}

pub fn hello() {
    let pi = 3.14;
    println!("Hello {} {}", inc(pi), inc(-pi));
}
