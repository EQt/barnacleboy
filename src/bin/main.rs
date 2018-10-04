extern crate merfishtools;
extern crate itertools;
extern crate image;
extern crate palette;
extern crate cogset;
extern crate rand;

use rand::{thread_rng, Rng};


use palette::{Srgba, Hsla};

use merfishtools::io::merfishdata::Reader;
use merfishtools::io::merfishdata::binary::Reader as MReader;
use itertools::Itertools;
use image::Pixel;
use merfishtools::io::merfishdata::binary::Record;
use std::collections::HashMap;
use cogset::{Optics, BruteScan, Euclid, Dbscan, Kmeans};

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

    // Find cells by applying optics clustering
    let mut reader = MReader::from_file(path).unwrap();
    let points: Vec<Euclid<[f64; 2]>> = reader.records().into_iter().map(|r| r.unwrap())
        .filter(|r| r.in_nucleus == 1)
        .map(|r| r.abs_position)
        .filter(|[x, y]| x - min_x < 500. && y - min_y < 500.)
        .map(|[x, y]| Euclid([(x - min_x) as f64, (y - min_y) as f64]))
        .collect();

    println!("Num points: {}", points.len());

    let scanner = BruteScan::new(&points);
    let eps = 4.;
    let min_pts = 30;

//    let mut dbscan = Dbscan::new(scanner, eps, 2);
//    let clusters = dbscan.by_ref().collect::<Vec<_>>();

    let optics = Optics::new(scanner, eps, min_pts);
    let mut clustering = optics.dbscan_clustering(eps);
    let mut clusters = clustering.by_ref().collect::<Vec<_>>();
    let noise = clustering.noise_points();

//    let k = 75;
//    let kmeans = Kmeans::new(&points, k);
//    let mut clusters: Vec<Vec<usize>> = kmeans.clusters().into_iter().map(|(kmean, points)| points).collect();


    let mut img = image::ImageBuffer::from_pixel(abs_width, abs_height, image::Rgba([0u8, 0u8, 0u8, 255u8]));
    let num_clusters = clusters.len();
    println!("Num clusters: {}", num_clusters);
    thread_rng().shuffle(&mut clusters);
    for (i, cluster) in clusters.into_iter().enumerate() {
        let color = Hsla::new(((i as f32) / (num_clusters as f32)) * 360., 1.0, 0.5, 0.75);
        let color = Srgba::from(color);
        let data = [(color.color.red * 255.) as u8, (color.color.green * 255.) as u8, (color.color.blue * 255.) as u8, (color.alpha * 255.) as u8];
        let rgba = image::Rgba(data);

        for point_idx in cluster {
            let Euclid(point) = points[point_idx];
            let [x, y] = point;
            let mut pixel: &mut image::Rgba<u8> = img.get_pixel_mut(x.floor() as u32, y.floor() as u32);
            pixel.blend(&rgba);
        }
    }
    for &point_idx in noise {
        let Euclid(point) = points[point_idx];
        let [x, y] = point;
        let data = [255, 255, 255, 128];
        let rgba = image::Rgba(data);
        let mut pixel: &mut image::Rgba<u8> = img.get_pixel_mut(x.floor() as u32, y.floor() as u32);
        pixel.blend(&rgba);
    }

    image::ImageRgba8(image::imageops::rotate90(&img)).save(format!("img/{}.png", "clusters")).unwrap();

    std::process::exit(0);

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
    image::ImageRgba8(image::imageops::rotate90(&img)).save(format!("img/{}.png", "absolute")).unwrap();
}
