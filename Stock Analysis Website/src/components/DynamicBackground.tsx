import { motion } from "motion/react";

export function DynamicBackground() {
  return (
    <div className="fixed inset-0 overflow-hidden pointer-events-none -z-10">
      {/* Animated gradient blobs */}
      <motion.div
        className="absolute rounded-full blur-3xl opacity-20"
        style={{
          width: "600px",
          height: "600px",
          background: "radial-gradient(circle, #3E8EDE 0%, transparent 70%)",
          top: "-10%",
          left: "-10%",
        }}
        animate={{
          x: [0, 100, 0],
          y: [0, 150, 0],
          scale: [1, 1.2, 1],
        }}
        transition={{
          duration: 20,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />

      <motion.div
        className="absolute rounded-full blur-3xl opacity-15"
        style={{
          width: "500px",
          height: "500px",
          background: "radial-gradient(circle, #5BA4F0 0%, transparent 70%)",
          top: "50%",
          right: "-10%",
        }}
        animate={{
          x: [0, -80, 0],
          y: [0, -100, 0],
          scale: [1, 1.3, 1],
        }}
        transition={{
          duration: 25,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />

      <motion.div
        className="absolute rounded-full blur-3xl opacity-10"
        style={{
          width: "700px",
          height: "700px",
          background: "radial-gradient(circle, #2C6BAA 0%, transparent 70%)",
          bottom: "-20%",
          left: "30%",
        }}
        animate={{
          x: [0, -50, 0],
          y: [0, 80, 0],
          scale: [1, 1.1, 1],
        }}
        transition={{
          duration: 30,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />

      {/* Floating particles */}
      {[...Array(15)].map((_, i) => (
        <motion.div
          key={i}
          className="absolute rounded-full"
          style={{
            width: `${Math.random() * 6 + 2}px`,
            height: `${Math.random() * 6 + 2}px`,
            backgroundColor: "#3E8EDE",
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`,
            opacity: 0.1,
          }}
          animate={{
            y: [0, -30, 0],
            x: [0, Math.random() * 20 - 10, 0],
            opacity: [0.1, 0.3, 0.1],
          }}
          transition={{
            duration: Math.random() * 10 + 10,
            repeat: Infinity,
            ease: "easeInOut",
            delay: Math.random() * 5,
          }}
        />
      ))}

      {/* Animated grid overlay */}
      <motion.div
        className="absolute inset-0 opacity-5"
        style={{
          backgroundImage: `
            linear-gradient(#3E8EDE 1px, transparent 1px),
            linear-gradient(90deg, #3E8EDE 1px, transparent 1px)
          `,
          backgroundSize: "50px 50px",
        }}
        animate={{
          opacity: [0.03, 0.08, 0.03],
        }}
        transition={{
          duration: 8,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />
    </div>
  );
}
