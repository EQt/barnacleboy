#!/bin/sh
for f in barcode_*.png; do convert "$f" -crop 512x512+0+0 +repage -fill white -draw "text 20,20 '$f'" "crop_$f"; done
convert -delay 33 crop_barcode_*.png -coalesce crop_barcode.gif
