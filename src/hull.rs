extern crate merfishtools;
extern crate num_traits;
extern crate rayon;

use self::merfishtools::io::merfishdata::binary::Record;
use self::num_traits::identities::Zero;
use self::rayon::join;
use std::collections::HashSet;
use std::hash::Hash;
use std::hash::Hasher;
use std::cmp::Ordering;

trait Joiner {
    fn is_parallel() -> bool;
    fn join<A, RA, B, RB>(oper_a: A, oper_b: B) -> (RA, RB)
        where A: FnOnce() -> RA + Send, B: FnOnce() -> RB + Send, RA: Send, RB: Send;
}

struct Parallel;

impl Joiner for Parallel {
    #[inline]
    fn is_parallel() -> bool {
        true
    }
    #[inline]
    fn join<A, RA, B, RB>(oper_a: A, oper_b: B) -> (RA, RB)
        where A: FnOnce() -> RA + Send, B: FnOnce() -> RB + Send, RA: Send, RB: Send
    {
        rayon::join(oper_a, oper_b)
    }
}

struct Sequential;

impl Joiner for Sequential {
    #[inline]
    fn is_parallel() -> bool {
        false
    }
    #[inline]
    fn join<A, RA, B, RB>(oper_a: A, oper_b: B) -> (RA, RB)
        where A: FnOnce() -> RA + Send, B: FnOnce() -> RB + Send
    {
        let a = oper_a();
        let b = oper_b();
        (a, b)
    }
}

#[derive(Clone, PartialEq, Eq, Hash, PartialOrd, Debug)]
struct Point {
    x: isize,
    y: isize,
}

fn side(p: &Point, a: &Point, b: &Point) -> i8 {
    let Point { x: p1, y: p2 } = p;
    let Point { x: a1, y: a2 } = a;
    let Point { x: b1, y: b2 } = b;
    let val = (p2 - a2) * (b1 - a1) - (b2 - a2) * (p1 - a1);
    match val {
        x if x == 0 => 0,
        x if x < 0 => -1,
        x if x > 0 => 1,
        _ => panic!("x is neither negative, nor positive, nor zero")
    }
}

#[inline]
fn distance_from_point(a: &Point, b: &Point) -> f32 {
    ((a.y - b.y) as f32).powi(2) + ((a.x - b.x) as f32).powi(2)
}

#[inline]
fn distance_from_line(p: &Point, a: &Point, b: &Point) -> f32 {
    (((p.y - a.y) * (b.x - a.x) - (b.y - a.y) * (p.x - a.x)) as f32).abs()
}

fn _quick_hull<'a, J: Joiner>(points: &'a [Point], p1: &'a Point, p2: &'a Point, s: i8) -> HashSet<&'a Point> {
    if J::is_parallel() && points.len() <= 5 * 1024 {
        return _quick_hull::<Sequential>(points, p1, p2, s);
    }

    // find point with max distance from line p1–p2
    if let (Some(point), max_dist) = points.iter()
        .filter(|&p| side(p, p1, p2) == s)
        .map(|p| (p, distance_from_line(p, p1, p2)))
        .fold((None, 0.), |acc, (p, dist)| {
            if dist > acc.1 {
                (Some(p), dist)
            } else {
                acc
            }
        }) {
        let v = side(point, p1, p2);
        let (mut l, mut r) = join(|| _quick_hull::<J>(points, point, p1, -v),
                                  || _quick_hull::<J>(points, point, p2, v));
        l.union(&r).into_iter().cloned().collect()
    } else {
        // if no such point exists, add line ends to hull
        let mut v = HashSet::new();
        v.insert(p1);
        v.insert(p2);
        v
    }
}

fn quick_hull(points: &[Point]) -> HashSet<&Point> {
    let min_x = points.iter().fold(None, |acc, p| {
        match acc {
            None => Some(p),
            Some(o) if p.x < o.x => Some(p),
            Some(o) if p.x >= o.x => Some(o),
            _ => None
        }
    }).unwrap();
    let max_x = points.iter().fold(None, |acc, p| {
        match acc {
            None => Some(p),
            Some(o) if p.x >= o.x => Some(p),
            Some(o) if p.x < o.x => Some(o),
            _ => None
        }
    }).unwrap();
    let (mut l, mut r) = rayon::join(|| _quick_hull::<Parallel>(points, min_x, max_x, 1),
                                     || _quick_hull::<Parallel>(points, min_x, max_x, -1));
    l.union(&r).into_iter().cloned().collect()
}

#[cfg(test)]
mod tests {
    use hull::Point;
    use hull::quick_hull;

    #[test]
    fn it_works() {
        let points = vec![Point { x: 1, y: 1 }, Point { x: 0, y: 0 }, Point { x: 2, y: 0 }, Point { x: 1, y: -1 }, Point { x: 1, y: 0 }];
        let hull = quick_hull(&points[..]);
        assert!(!hull.contains(&Point { x: 1, y: 0 }));
    }
}