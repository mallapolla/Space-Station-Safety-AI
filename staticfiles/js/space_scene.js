const starfieldCanvas = document.getElementById("starfieldCanvas");

if (starfieldCanvas) {
    const context = starfieldCanvas.getContext("2d");
    const stars = [];
    const shootingStars = [];

    function resizeCanvas() {
        starfieldCanvas.width = window.innerWidth;
        starfieldCanvas.height = window.innerHeight;
    }

    function createStars() {
        stars.length = 0;
        const total = Math.max(90, Math.floor((window.innerWidth * window.innerHeight) / 18000));
        for (let index = 0; index < total; index += 1) {
            stars.push({
                x: Math.random() * starfieldCanvas.width,
                y: Math.random() * starfieldCanvas.height,
                radius: Math.random() * 1.8 + 0.3,
                speed: Math.random() * 0.18 + 0.04,
                alpha: Math.random() * 0.7 + 0.2,
                pulse: Math.random() * Math.PI * 2,
            });
        }
    }

    function spawnShootingStar() {
        shootingStars.push({
            x: Math.random() * starfieldCanvas.width * 0.7,
            y: Math.random() * starfieldCanvas.height * 0.45,
            length: Math.random() * 120 + 80,
            speedX: Math.random() * 7 + 8,
            speedY: Math.random() * 2.5 + 2,
            life: 1,
        });
    }

    function animate() {
        context.clearRect(0, 0, starfieldCanvas.width, starfieldCanvas.height);

        stars.forEach((star) => {
            star.y += star.speed;
            star.pulse += 0.015;

            if (star.y > starfieldCanvas.height) {
                star.y = -10;
                star.x = Math.random() * starfieldCanvas.width;
            }

            const glow = star.alpha + Math.sin(star.pulse) * 0.15;
            context.beginPath();
            context.fillStyle = `rgba(168, 235, 255, ${Math.max(0.15, glow)})`;
            context.arc(star.x, star.y, star.radius, 0, Math.PI * 2);
            context.fill();
        });

        if (Math.random() < 0.012 && shootingStars.length < 3) {
            spawnShootingStar();
        }

        for (let index = shootingStars.length - 1; index >= 0; index -= 1) {
            const star = shootingStars[index];
            context.strokeStyle = `rgba(123, 226, 255, ${star.life})`;
            context.lineWidth = 2;
            context.beginPath();
            context.moveTo(star.x, star.y);
            context.lineTo(star.x - star.length, star.y - star.length * 0.28);
            context.stroke();

            star.x += star.speedX;
            star.y += star.speedY;
            star.life -= 0.02;

            if (star.life <= 0) {
                shootingStars.splice(index, 1);
            }
        }

        window.requestAnimationFrame(animate);
    }

    resizeCanvas();
    createStars();
    animate();

    window.addEventListener("resize", () => {
        resizeCanvas();
        createStars();
    });
}

const parallaxItems = document.querySelectorAll("[data-parallax]");

if (parallaxItems.length) {
    let frameRequested = false;
    let mouseX = 0;
    let mouseY = 0;

    function applyParallax() {
        const centerX = window.innerWidth / 2;
        const centerY = window.innerHeight / 2;

        parallaxItems.forEach((item) => {
            const intensity = Number(item.dataset.parallax || 0);
            const offsetX = ((mouseX - centerX) / centerX) * intensity;
            const offsetY = ((mouseY - centerY) / centerY) * intensity;
            item.style.transform = `translate3d(${offsetX}px, ${offsetY}px, 0)`;
        });

        frameRequested = false;
    }

    window.addEventListener("mousemove", (event) => {
        mouseX = event.clientX;
        mouseY = event.clientY;

        if (!frameRequested) {
            frameRequested = true;
            window.requestAnimationFrame(applyParallax);
        }
    });
}
