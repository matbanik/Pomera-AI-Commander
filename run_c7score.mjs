import { getScore } from "@upstash/c7score";

async function main() {
    console.log("Running c7score for /matbanik/pomera-ai-commander...\n");

    try {
        const result = await getScore("/matbanik/pomera-ai-commander", {
            report: {
                console: true,
                humanReadable: true,
                returnScore: true
            }
        });

        console.log("\n=== FULL RESULT ===");
        console.log(JSON.stringify(result, null, 2));
    } catch (error) {
        console.error("Error:", error.message);
        console.error(error);
    }
}

main();
