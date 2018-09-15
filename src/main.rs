extern crate merfishtools;
extern crate itertools;
extern crate image;
extern crate palette;

use palette::{Srgba, Hsla};

use merfishtools::io::merfishdata::Reader;
use merfishtools::io::merfishdata::binary::Reader as MReader;
use itertools::Itertools;
use image::Pixel;
use merfishtools::io::merfishdata::binary::Record;
use std::collections::HashMap;

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let path = &args[1];
    // TODO: don't iterate twice.
    let mut reader = MReader::from_file(path).unwrap();
    let [[min_x, max_x], [min_y, max_y]] = reader.records().into_iter()
        .map(|r| r.unwrap())
        .fold([[std::f32::MAX, std::f32::MIN], [std::f32::MAX, std::f32::MIN]], |acc, r| {
            let [x, y] = r.abs_position;
            [[acc[0][0].min(x), acc[0][1].max(x)],
                [acc[1][0].min(y), acc[1][1].max(y)]]
        });
    let abs_width = (max_x - min_x).abs().ceil() as u32;
    let abs_height = (max_y - min_y).abs().ceil() as u32;
    let mut img = image::ImageBuffer::from_pixel(abs_width, abs_height, image::Rgba([0u8, 0u8, 0u8, 255u8]));
    println!("{}x{}", abs_width, abs_height);

    let mut reader = MReader::from_file(path).unwrap();
    let map: HashMap<u16, Vec<Record>> = reader.records().into_iter()
        .map(|r| r.unwrap())
        .map(|r| (r.barcode_id, r))
        .into_group_map();
    for (key, group) in map.into_iter() {
        let mut barcode_img = image::ImageBuffer::from_pixel(abs_width, abs_height, image::Rgba([0u8, 0u8, 0u8, 255u8]));
        for record in group {
            let [x, y] = record.abs_position;
            let [x, y] = [(x - min_x).floor() as u32, (y - min_y).floor() as u32];

//            let magnitude: u8 = (record.total_magnitude * 255.).floor() as u8;
            let color = Hsla::new(((key as f32) / 140.) * 360., 1.0, 0.5, 0.75);
            let color = Srgba::from(color);
            let data = [(color.color.red * 255.) as u8, (color.color.green * 255.) as u8, (color.color.blue * 255.) as u8, (color.alpha * 255.) as u8];
            let rgba = image::Rgba(data);

            let mut pixel: &mut image::Rgba<u8> = img.get_pixel_mut(x as u32, y as u32);
            pixel.blend(&rgba);

            let mut pixel: &mut image::Rgba<u8> = barcode_img.get_pixel_mut(x as u32, y as u32);
            pixel.blend(&rgba);
        }
        image::ImageRgba8(image::imageops::rotate90(&barcode_img)).save(format!("img/barcode_{}.png", key)).unwrap();
    }
    image::ImageRgba8(image::imageops::rotate90(&img)).save(format!("img/{}.png", "absolute")).unwrap();
}
