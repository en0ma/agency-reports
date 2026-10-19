// One-time local setup: creates backend/.env from the example if it doesn't exist yet.
import { copyFileSync, existsSync } from "node:fs";

const target = "backend/.env";
if (existsSync(target)) {
  console.log(`${target} already exists, leaving it alone.`);
} else {
  copyFileSync("backend/.env.example", target);
  console.log(`Created ${target} from backend/.env.example.`);
}
