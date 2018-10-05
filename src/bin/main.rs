extern crate image;
extern crate itertools;
extern crate merfishtools;
extern crate palette;
extern crate serde;
#[macro_use]
extern crate serde_derive;
extern crate serde_pickle;

use image::Pixel;
use itertools::Itertools;
use merfishtools::io::merfishdata::binary::Reader as MReader;
use merfishtools::io::merfishdata::binary::Record;
use merfishtools::io::merfishdata::Reader;
use palette::{Hsla, Srgba};
use std::collections::HashMap;


#[derive(Serialize, Deserialize, Debug)]
#[serde(rename_all = "camelCase")]
struct Cell {
    #[serde(rename = "FOVNum")]
    fovnum: f64,
    #[serde(rename = "cellID")]
    cell_id: f64,
    cytoplasm_area: f64,
    cytoplasm_boundary: Vec<(f64, f64)>,
    cytoplasm_convex_hull_ratio: f64,
    edge_marker: f64,
    nucleus_area: f64,
    nucleus_ave_intensity: f64,
    nucleus_ave_intensity0: f64,
    nucleus_boundary: Vec<(f64, f64)>,
    nucleus_convex_hull_ratio: f64,
}

fn main() {
    // TODO use clap.g
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

    // create plot for every single barcode
    let mut reader = MReader::from_file(path).unwrap();
    let map: HashMap<u16, Vec<Record>> = reader.records().into_iter()
        .map(|r| r.unwrap())
        .map(|r| (r.barcode_id, r))
        .into_group_map();
    for (key, group) in map.into_iter() {
        let mut barcode_img = image::ImageBuffer::from_pixel(abs_width, abs_height, image::LumaA([0u8, 255u8]));
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

            let mut pixel: &mut image::LumaA<u8> = barcode_img.get_pixel_mut(x as u32, y as u32);
            let grey = image::LumaA([255, (record.total_magnitude * 255.).floor() as u8]);
            pixel.blend(&grey);
        }
        if abs_height > abs_width {
            // We actually rotate the images 90° CW, so that width > height for better display properties.
            barcode_img = image::imageops::rotate90(&barcode_img)
        }
        let image_path = std::path::Path::new("img/");
        if !image_path.exists() {
            std::fs::create_dir(&image_path);
        }
        image::ImageLumaA8(barcode_img).save(format!("img/barcode_{}.png", key)).unwrap();
    }

    let f = std::fs::File::open("data/cellBoundaries.pickle").unwrap();
    let cell_boundaries: HashMap<String, Cell> = serde_pickle::from_reader(f).unwrap();
    for (_cell_id, cell) in cell_boundaries.iter() {
        // Skip virtual/non-existent cells (?) as well as non-cell boundaries
        if cell.edge_marker != 0. {
            continue;
        }
        let cbounds = &cell.cytoplasm_boundary;
        for (x, y) in cbounds {
            let (x, y) = (*x as f32, *y as f32);
            let (x, y) = ((x - min_x).floor() as u32, (y - min_y).floor() as u32);
            if x < abs_width && y < abs_height {
                let mut pixel: &mut image::Rgba<u8> = img.get_pixel_mut(x as u32, y as u32);
                let white = image::Rgba([255, 255, 255, 255]);
                pixel.blend(&white);
            }
        }

        let nbounds = &cell.nucleus_boundary;
        for (x, y) in nbounds {
            let (x, y) = (*x as f32, *y as f32);
            let (x, y) = ((x - min_x).floor() as u32, (y - min_y).floor() as u32);
            if x < abs_width && y < abs_height {
                let mut pixel: &mut image::Rgba<u8> = img.get_pixel_mut(x as u32, y as u32);
                let white = image::Rgba([255, 255, 255, 255]);
                pixel.blend(&white);
            }
        }
    }
    if abs_height > abs_width {
        // We actually rotate the images 90° CW, so that width > height for better display properties.
        img = image::imageops::rotate90(&img)
    }
    image::ImageRgba8(img).save(format!("img/{}.png", "absolute")).unwrap();
}
