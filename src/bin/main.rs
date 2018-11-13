extern crate image;
extern crate itertools;
extern crate merfishtools;
extern crate palette;
extern crate rayon;
extern crate serde;
#[macro_use]
extern crate serde_derive;
extern crate serde_pickle;
extern crate structopt;

use image::Pixel;
use itertools::Itertools;
use merfishtools::io::merfishdata::binary::Reader as MReader;
use merfishtools::io::merfishdata::binary::Record;
use merfishtools::io::merfishdata::Reader;
use palette::{Hsla, Srgba};
use rayon::prelude::*;
use std::collections::HashMap;
use std::path::PathBuf;
use structopt::StructOpt;

#[derive(StructOpt, Debug)]
#[structopt(name = "basic")]
struct Options {
    #[structopt(name = "FILE", parse(from_os_str))]
    input: PathBuf,
    #[structopt(short = "b", long = "boundaries", parse(from_os_str))]
    boundaries: Option<PathBuf>,
    #[structopt(short = "o", long = "out", parse(from_os_str), default_value = "img/")]
    output: PathBuf,
}

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

fn draw_points<P: image::Pixel, I: image::GenericImage<Pixel=P>>(img: &mut I, color: &P, points: &Vec<(u32, u32)>) {
    points.iter().for_each(|(x, y)| img.get_pixel_mut(*x, *y).blend(&color));
}

fn main() {
    let opt = Options::from_args();
    let merfish_path = &opt.input;

    let image_path = std::path::Path::new(&opt.output);
    if !image_path.exists() {
        std::fs::create_dir(&image_path).expect(&format!("Failed creating directory {:?}.", &image_path));
    }

    // TODO: don't iterate twice.
    println!("reading {:?}", merfish_path);
    let mut reader = MReader::from_file(merfish_path).unwrap();
    let [[min_x, max_x], [min_y, max_y]] = reader.records().into_iter()
        .map(|r| r.unwrap())
        .fold([[std::f32::MAX, std::f32::MIN], [std::f32::MAX, std::f32::MIN]], |acc, r| {
            let [x, y] = r.abs_position;
            [[acc[0][0].min(x), acc[0][1].max(x)],
                [acc[1][0].min(y), acc[1][1].max(y)]]
        });
    println!("x = {} {}", min_x, max_x);
    println!("y = {} {}", min_y, max_y);

    let abs_width = (max_x - min_x).abs().ceil() as u32;
    let abs_height = (max_y - min_y).abs().ceil() as u32;
    let mut img = image::ImageBuffer::from_pixel(abs_width, abs_height, image::Rgba([0u8, 0u8, 0u8, 255u8]));
    println!("{}x{}", abs_width, abs_height);

    let mut cytoplasm_boundaries = None;
    let mut nucleus_boundaries = None;
    // Get cell boundaries if available
    if let Some(cell_boundaries_path) = &opt.boundaries {
        println!("reading cell boundaries {:?}", cell_boundaries_path);
        let f = std::fs::File::open(cell_boundaries_path).unwrap();
        let cell_boundaries: HashMap<String, Cell> = serde_pickle::from_reader(f).unwrap();
        // Skip virtual/non-existent cells (?) as well as non-cell boundaries
        cytoplasm_boundaries = Some(cell_boundaries.values()
            .filter(|&cell| cell.edge_marker != 1.)
            .flat_map(|cell| &cell.cytoplasm_boundary)
            .map(|&(x, y)| { ((x as f32 - min_x).floor() as u32, (y as f32 - min_y).floor() as u32) })
            .collect());
        nucleus_boundaries = Some(cell_boundaries.values()
            .filter(|&cell| cell.edge_marker != 1.)
            .flat_map(|cell| &cell.nucleus_boundary)
            .map(|&(x, y)| { ((x as f32 - min_x).floor() as u32, (y as f32 - min_y).floor() as u32) })
            .collect());
    }

    let transparent_white_rgba = image::Rgba([255, 255, 255, 128]);
    let transparent_white_lumaa = image::LumaA([255, 128]);

    // create plot for every single barcode
    let mut reader = MReader::from_file(merfish_path).unwrap();
    let map: HashMap<u16, Vec<Record>> = reader.records().into_iter()
        .map(|r| r.unwrap())
        .map(|r| (r.barcode_id, r))
        .into_group_map();

    map.par_iter().for_each(|(&key, ref group)| {
        let mut barcode_img = image::ImageBuffer::from_pixel(abs_width, abs_height, image::LumaA([0u8, 255u8]));
        for record in group.iter() {
            let [x, y] = record.abs_position;
            let [x, y] = [(x - min_x).floor() as u32, (y - min_y).floor() as u32];
            let mut pixel: &mut image::LumaA<u8> = barcode_img.get_pixel_mut(x as u32, y as u32);
            let data = [255, 255u8.min(1u8.max((record.total_magnitude * 255.).floor() as u8))];
            let lumaa = image::LumaA(data);
            pixel.blend(&lumaa);
        }
        if let Some(ref bounds) = cytoplasm_boundaries {
            draw_points(&mut barcode_img, &transparent_white_lumaa, &bounds);
        }
        if let Some(ref bounds) = nucleus_boundaries {
            draw_points(&mut barcode_img, &transparent_white_lumaa, &bounds);
        }
        if abs_height > abs_width {
            // We actually rotate the images 90° CW, so that width > height for better display properties.
            barcode_img = image::imageops::rotate90(&barcode_img)
        }

        image::ImageLumaA8(barcode_img).save(image_path.join(format!("barcode_{:03}.png", key))).unwrap();
    });

    map.iter().for_each(|(&key, ref group)| {
        for record in group.iter() {
            let [x, y] = record.abs_position;
            let [x, y] = [(x - min_x).floor() as u32, (y - min_y).floor() as u32];
//            let magnitude: u8 = (record.total_magnitude * 255.).floor() as u8;
            let color = Hsla::new(((key as f32) / 140.) * 360., 1.0, 0.5, 0.75);
            let color = Srgba::from(color);
            let mut pixel: &mut image::Rgba<u8> = img.get_pixel_mut(x as u32, y as u32);
            let data = [(color.color.red * 255.) as u8, (color.color.green * 255.) as u8, (color.color.blue * 255.) as u8, (color.alpha * 255.) as u8];
            let rgba = image::Rgba(data);
            pixel.blend(&rgba);
        }
    });
    if let Some(ref bounds) = cytoplasm_boundaries {
        draw_points(&mut img, &transparent_white_rgba, &bounds);
    }
    if let Some(ref bounds) = nucleus_boundaries {
        draw_points(&mut img, &transparent_white_rgba, &bounds);
    }

    if abs_height > abs_width {
        // We actually rotate the images 90° CW, so that width > height for better display properties.
        img = image::imageops::rotate90(&img)
    }
    image::ImageRgba8(img).save(image_path.join("all.png")).unwrap();
}
