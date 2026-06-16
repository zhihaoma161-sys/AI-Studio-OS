const assert = require("node:assert/strict");
const { chromium } = require(process.env.AI_STUDIO_PLAYWRIGHT_MODULE);

async function main() {
  const baseUrl = process.env.AI_STUDIO_SELFTEST_URL;
  const browser = await chromium.launch({
    headless: true,
    executablePath: process.env.AI_STUDIO_EDGE_PATH,
  });
  let projectRevision = 1;
  let history = [{ id: "r0001_ui_snapshot", revision: 1 }];
  let analysisCount = 0;
  let folderOpenCalls = 0;
  let rollbackCalls = 0;
  let applyPayload = null;

  try {
  const page = await browser.newPage();
  page.on("dialog", async (dialog) => dialog.accept());

  await page.route("**/api/settings/llm", async (route) => {
    await route.fulfill({
      json: {
        configured: true,
        provider: "custom",
        base_url: "https://example.invalid/v1",
        model: "selftest",
        api_key_masked: "sk-********test",
      },
    });
  });
  await page.route("**/api/projects", async (route) => {
    await route.fulfill({
      json: {
        projects: [{
          system_id: "selftest-item-system",
          system_name: "无人值守测试道具系统",
          revision: projectRevision,
          lifecycle: "active",
          latest_change: projectRevision === 1 ? "initial" : "chg_ui_2",
          history_count: history.length,
          history,
          files: [
            "system_design_detail.md",
            "ui_interaction_blueprint.md",
            "system_numerical_data.json",
            "system_numerical_docs.json",
          ],
          iterable_files: [
            "system_design_detail.md",
            "ui_interaction_blueprint.md",
            "system_numerical_data.json",
            "system_numerical_docs.json",
          ],
        }],
      },
    });
  });
  await page.route("**/api/open_project_folder", async (route) => {
    folderOpenCalls += 1;
    await route.fulfill({ json: { ok: true, path: "C:\\isolated\\current" } });
  });
  await page.route("**/api/changes/analyze", async (route) => {
    analysisCount += 1;
    const body = route.request().postDataJSON();
    const discussion = [{ kind: "requirement", content: body.requirement }];
    if (body.analysis_feedback) {
      discussion.push({ kind: "feedback", content: body.analysis_feedback });
    }
    const supervisorPlan = {
      files: [
        {
          file: "system_design_detail.md",
          reason: "出售功能需要补充系统详细规则",
          agent: "system_planner",
          required: true,
          writable: true,
        },
        {
          file: "ui_interaction_blueprint.md",
          reason: "点击、批量选择和预览结果涉及 UX",
          agent: "ux_agent",
          required: true,
          writable: true,
        },
        {
          file: "system_numerical_data.json",
          reason: "需要新增出售价格字段",
          agent: "numerical_planner",
          required: true,
          writable: true,
        },
        {
          file: "system_numerical_docs.json",
          reason: "新增数值字段必须同步说明",
          agent: "numerical_planner",
          required: true,
          writable: true,
        },
      ],
      warnings: [],
    };
    const baseAnalysis = {
      ok: true,
      change_id: `chg_ui_${analysisCount}`,
      requirement: body.requirement,
      analysis_feedback: body.analysis_feedback || "",
      discussion,
      selected_document: body.selected_document,
      impact_confirmed: body.impact_confirmed === true,
      writable_files: [
        "system_design_detail.md",
        "ui_interaction_blueprint.md",
        "system_numerical_data.json",
        "system_numerical_docs.json",
      ],
      reference_files: [],
      affected_agents: ["system_planner", "ux_agent", "numerical_planner"],
      dependent_systems: [],
      supervisor_plan: supervisorPlan,
      duration_ms: 10,
      trace_id: `ui_trace_${analysisCount}`,
    };
    if (body.impact_confirmed !== true) {
      await route.fulfill({
        json: {
          ...baseAnalysis,
          requires_impact_confirmation: true,
        },
      });
      return;
    }
    const proposal = {
      text_changes: [{
        file: "system_design_detail.md",
        anchor: "道具使用",
        content: "新增出售流程：玩家可批量选择道具并预览出售结果。",
        deprecated: "",
      }, {
        file: "ui_interaction_blueprint.md",
        anchor: "背包操作",
        content: "新增出售按钮、批量选择态与出售预览弹窗。",
        deprecated: "",
      }],
      numerical_operations: [{
        action: "add_column",
        table: "item_table",
        column: "sell_price",
        default: 0,
      }],
      numerical_doc_changes: [{
        table: "item_table",
        field: "sell_price",
        description: "道具出售价格。",
      }],
    };
    await route.fulfill({
      json: {
        ok: true,
        change_id: `chg_ui_${analysisCount}`,
        requirement: body.requirement,
        analysis_feedback: body.analysis_feedback || "",
        discussion,
        selected_document: body.selected_document,
        writable_files: ["system_design_detail.md", "system_numerical_data.json"],
        reference_files: [],
        affected_agents: ["system_planner", "numerical_planner"],
        dependent_systems: [],
        proposal_incomplete: analysisCount === 2,
        proposal_warnings: analysisCount === 2 ? ["ignored invalid optional update_rows"] : [],
        preview: {
          text_changes: [{
            file: "system_design_detail.md",
            anchor: "道具使用",
            content: "新增出售流程",
            deprecated: "",
          }],
          numerical_operations: [{
            action: "add_column",
            table: "item_table",
            column: "sell_price",
            default: 0,
          }],
        },
        ...baseAnalysis,
        requires_impact_confirmation: false,
        proposal_incomplete: analysisCount === 4,
        proposal_warnings: analysisCount === 4 ? ["ignored invalid optional update_rows"] : [],
        proposal,
        preview: proposal,
        duration_ms: 10,
        trace_id: `ui_trace_${analysisCount}`,
      },
    });
  });
  await page.route("**/api/changes/apply", async (route) => {
    applyPayload = route.request().postDataJSON();
    projectRevision = 2;
    history = [{ id: "r0001_ui_snapshot", revision: 1 }];
    await route.fulfill({ json: { ok: true, revision: 2 } });
  });
  await page.route("**/api/projects/*/rollback", async (route) => {
    rollbackCalls += 1;
    projectRevision = 1;
    history = [];
    await route.fulfill({ json: { ok: true, revision: 1 } });
  });

  await page.goto(baseUrl, { waitUntil: "domcontentloaded" });
  await page.locator('[data-tab="iterate"]').click();
  await page.locator("#iterationConversation").filter({ hasText: "[System] 等待引擎启动..." }).waitFor();
  await page.locator('[data-tab="history"]').click();
  await page.locator("#projectList .proj-title").waitFor();
  await page.locator("#projectList .proj-title").click();
  assert.equal(folderOpenCalls, 1, "clicking project title must request its folder");

  await page.locator("#projectList .proj-folder .mini-btn").first().click();
  await page.locator("#projectList .proj-file button").first().click();
  await page.locator("#iterationType").selectOption("new_feature");
  assert.equal(await page.locator("#iterationProject").inputValue(), "selftest-item-system");
  assert.equal(await page.locator("#iterationDocument").inputValue(), "system_design_detail.md");

  await page.locator("#iterationInput").fill("新增道具出售功能");
  await page.locator("#iterationSubmitBtn").click();
  await page.locator("#iterationAnalysis").waitFor({ state: "visible" });
  assert.equal(await page.locator("#iterationInput").inputValue(), "");
  assert.equal(await page.locator("#iterationConversation .iteration-message").count(), 1);
  const firstMessageBox = await page.locator("#iterationConversation .iteration-message").first().boundingBox();
  assert.ok(firstMessageBox && firstMessageBox.height < 90, "short message background should fit content height");
  await page.locator("#iterationSupervisorPreview").filter({ hasText: "system_numerical_docs.json" }).waitFor();
  assert.equal(await page.locator("#iterationApplyBtn").isDisabled(), true, "apply is disabled before impact confirmation");
  assert.equal(await page.locator("#iterationConfirmImpactBtn").isDisabled(), false, "impact confirmation is enabled after supervisor split");

  await page.locator("#iterationConfirmImpactBtn").click();
  await page.locator("#iterationNumberPreview").filter({ hasText: "数值说明变更" }).waitFor();
  await page.waitForFunction(() => !document.getElementById("iterationApplyBtn").disabled);
  assert.equal(await page.locator("#iterationApplyBtn").isDisabled(), false, "apply is enabled after complete preview");

  await page.locator("#iterationInput").fill("补充出售价格配置");
  await page.locator("#iterationSubmitBtn").click();
  await page.locator("#iterationConversation .iteration-message").nth(1).waitFor();
  assert.equal(await page.locator("#iterationInput").inputValue(), "");
  assert.equal(await page.locator("#iterationConversation .iteration-message").count(), 2);
  assert.equal(analysisCount, 3);
  await page.locator("#iterationSummary").filter({ hasText: "ui_trace_3" }).waitFor();
  assert.equal(await page.locator("#iterationApplyBtn").isDisabled(), true, "apply is disabled during second supervisor split");
  await page.locator("#iterationConfirmImpactBtn").click();
  await page.locator("#iterationSummary").filter({ hasText: "ui_trace_4" }).waitFor();
  await page.waitForFunction(() => !document.getElementById("iterationApplyBtn").disabled);
  assert.equal(analysisCount, 4);
  assert.equal(await page.locator("#iterationApplyBtn").isDisabled(), false, "apply stays enabled after second confirmed preview");

  await page.locator("#iterationApplyBtn").click();
  await page.locator("#iterationStatus").filter({ hasText: "r2" }).waitFor();
  assert.ok(applyPayload && Array.isArray(applyPayload.numerical_doc_changes), "apply sends numerical doc changes");
  await page.locator('[data-tab="history"]').click();
  await page.locator("#projectList .proj-title").filter({ hasText: "r2" }).waitFor();
  await page.locator("#projectList .history-meta .mini-btn").first().click();
  await page.locator("#projectList .proj-title").filter({ hasText: "r1" }).waitFor();
  assert.equal(rollbackCalls, 1);

    console.log(JSON.stringify({
      ok: true,
      analysisCount,
      folderOpenCalls,
      rollbackCalls,
      messages: 2,
      finalRevision: projectRevision,
    }));
  } finally {
    await browser.close();
  }
}

main().catch((error) => {
  console.error(error.stack || error);
  process.exitCode = 1;
});
