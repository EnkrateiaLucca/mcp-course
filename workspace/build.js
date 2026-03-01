const globalModules = '/Users/greatmaster/.nvm/versions/node/v22.14.0/lib/node_modules';
const pptxgen = require(globalModules + '/pptxgenjs');
const html2pptx = require('/Users/greatmaster/.claude/skills/pptx/scripts/html2pptx');
const path = require('path');

async function createPresentation() {
    const pptx = new pptxgen();
    pptx.layout = 'LAYOUT_16x9';
    pptx.author = 'Lucas Soares';
    pptx.title = 'Agent Basics - Building AI Agents with MCP';

    const slidesDir = path.join(__dirname, 'slides');

    // Slide 1: Title (HTML-based for text layout)
    await html2pptx(path.join(slidesDir, 'slide1.html'), pptx);

    // Slide 2: User <-> LLM diagram + ChatGPT screenshot
    await html2pptx(path.join(slidesDir, 'slide2.html'), pptx);

    // Slide 3: Tool Use diagram + web search screenshot
    await html2pptx(path.join(slidesDir, 'slide3.html'), pptx);

    // Slides 4-7: Full-slide agent architecture diagrams
    const agentDiagrams = [
        { file: 'diagram-agent-step1.png', notes: 'Step 1: LLM API Access' },
        { file: 'diagram-agent-step2.png', notes: 'Step 2: Connection to Tools/Resources' },
        { file: 'diagram-agent-step3.png', notes: 'Step 3: The Agent Logic' },
        { file: 'diagram-agent-complete.png', notes: 'Complete Agent Architecture' },
    ];

    for (const { file, notes } of agentDiagrams) {
        const slide = pptx.addSlide();
        // Cream background matching brand
        slide.background = { color: 'F5F3EB' };
        // Full-slide image (10" x 5.625" for 16:9)
        slide.addImage({
            path: path.join(slidesDir, file),
            x: 0, y: 0, w: 10, h: 5.625,
            sizing: { type: 'contain', w: 10, h: 5.625 }
        });
        slide.addNotes(notes);
    }

    // Slides 8-11: MCP integration diagrams (full-slide images)
    const mcpDiagrams = [
        { file: 'diagram-mcp-basic.png', notes: 'MCP Basic Concept: LLM → MCP → Context' },
        { file: 'diagram-mcp-mn-problem.png', notes: 'The M×N Integration Problem' },
        { file: 'diagram-mcp-mn-lines.png', notes: 'M×N: Each line is a separate integration' },
        { file: 'diagram-mcp-mn-solution.png', notes: 'MCP Solution: M+N integrations' },
    ];

    for (const { file, notes } of mcpDiagrams) {
        const slide = pptx.addSlide();
        slide.background = { color: 'F5F3EB' };
        slide.addImage({
            path: path.join(slidesDir, file),
            x: 0, y: 0, w: 10, h: 5.625,
            sizing: { type: 'contain', w: 10, h: 5.625 }
        });
        slide.addNotes(notes);
    }

    const outputPath = '/Users/greatmaster/Desktop/projects/oreilly-live-trainings/mcp-course/agent-basics.pptx';
    await pptx.writeFile({ fileName: outputPath });
    console.log('Presentation saved to:', outputPath);
}

createPresentation().catch(console.error);
