"use client";
import React from "react";
import styles from "./PersonaCompass.module.css"; // Import CSS module for styling

type PersonaCompassProps = {
  x: number;
  y: number;
};

const PersonaCompass = ({ x, y }: PersonaCompassProps) => {
  // Normalize the coordinates to fit within the grid (0 to 1 scale to 0% to 100%)
  const normalize = (value: number) => Math.min(1, Math.max(0, value)) * 100;

  return (
    <div className={styles.container}>
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
          <span className={styles.labelTop}>Authoritarian</span>
          <span className={styles.labelBottom}>Libertarian</span>
          <span className={styles.labelLeft}>Left</span>
          <span className={styles.labelRight}>Right</span>
        </div>
      </div>
    </div>
  );
};

export default PersonaCompass;
