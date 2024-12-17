"use client";
import React from "react";
import Compass from "@/models/opinions/Compass";
import styles from "./PersonaCompass.module.css"; // Import CSS module for styling

const PersonaCompass = ({
  x,
  y,
  name,
  labelTop,
  labelBottom,
  labelLeft,
  labelRight,
}: Compass) => {
  // Normalize the coordinates to fit within the grid (0 to 1 scale to 0% to 100%)
  const normalize = (value: number) => Math.min(1, Math.max(0, value)) * 100;

  return (
    <div className={styles.container}>
      <p className="text-center text-xl mb-5">{name}</p>
      {/* Compass grid */}
      <div className={styles.grid}>
        {/* Dot representing the x and y coordinates */}
        <div
          className={styles.dot}
          style={{
            left: `${normalize(x)}%`, // Map x to percentage (0 to 100)
            top: `${100 - normalize(y)}%`, // Map y to percentage (invert to align top-bottom correctly)
          }}
        ></div>

        {/* Labels */}
        <div className={styles.labelContainer}>
          <span className={styles.labelTop}>{labelTop}</span>
          <span className={styles.labelBottom}>{labelBottom}</span>
          <span className={styles.labelLeft}>{labelLeft}</span>
          <span className={styles.labelRight}>{labelRight}</span>
        </div>
      </div>
    </div>
  );
};

export default PersonaCompass;
