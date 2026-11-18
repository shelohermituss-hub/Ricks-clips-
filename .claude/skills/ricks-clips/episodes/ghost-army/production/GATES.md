# Quality gates — ghost-army (preview phase, 2026-11-18)

| gate | check | status | evidence |
|---|---|---|---|
| A_PREPRODUCTION | script_locked | **PASS** | SCRIPT.md, voice/script.txt |
| A_PREPRODUCTION | look_bible_exists | **PASS** | official fortress standard; references/REFERENCE_LOOK_BIBLE.md, episodes/ghost-army/STORY_BIBLE.md |
| A_PREPRODUCTION | shot_list_exists | **PASS** | film.json takes=11 |
| A_PREPRODUCTION | action_effect_matrix_exists | **PASS** | 9 story events in production/ACTION_EFFECT_MATRIX.json |
| B_ASSETS | hero_asset_inventory_complete | **PASS** | 7 hero assets registered |
| B_ASSETS | hero_assets_not_placeholder | **WARN** | Real tanks at the crossing: 73 parts, 5712 tris, 96% primitive generators, 72 textured mats -> primitive assembly / below hero detail; Sound half-track with horn speaker: 39 parts, 7080 tris, 95% primitive generators, 5 textured mats -> primitive assembly / below hero detail; Farmer's and boy's bicycles: flat 2D library prop, not a 3D asset; Field radio, Morse key, fist card: 1 parts, 12 tris, 100 |
| B_ASSETS | license_and_provenance_recorded | **PASS** | 10 assets with provenance |
| B_ASSETS | renderer_import_test_passed | **PASS** | 1/1 external assets render-tested |
| B_ASSETS | textures_verified | **PASS** | field 58/70 textured materials; camp 170/259 textured materials; road 190/246 textured materials; radio 26/32 textured materials; cafe 47/80 textured materials; photo 13/31 textured materials; river 405/529 textured materials; bedroom 34/48 textured materials; attic 36/53 textured materials |
| C_ENVIRONMENTS | detail_score_minimum_3 | **WARN** | below 3: field.geometry=2, camp.geometry=2, radio.geometry=2, radio.depth=2, photo.geometry=2, photo.depth=2, river.geometry=2; 9/9 places scored |
| C_ENVIRONMENTS | three_depth_planes | **WARN** | 7/9 places depth>=3 |
| C_ENVIRONMENTS | materials_reviewed | **PASS** | 9/9 places reviewed |
| C_ENVIRONMENTS | lighting_reviewed | **PASS** | 9/9 places reviewed |
| C_ENVIRONMENTS | environment_motion_reviewed | **WARN** | 9/9 places reviewed |
| D_ANIMATION | actions_have_animation | **PASS** | {"STATIC": 0, "WALK2F": 0, "GLIDE": 0, "POP": 0, "LIBRARY": 57, "OVERLAP": 0, "acts": 73, "status": "PASS"} |
| D_ANIMATION | contacts_checked | **WARN** | 2 frame-check FAIL groups, 2 waived with a reason (QA_LOG waivers) |
| D_ANIMATION | transitions_checked | **PASS** | film.tween={'ones': True, 'face_frames': 0, 'move_blend': 6} |
| D_ANIMATION | micro_animation_reviewed | **PASS** | motion_polish={'enabled': True, 'head_follow': 0.14, 'hand_follow': 0.08, 'breath': 0.55, 'breath_rate': 2.15, 'auto_blink': True} |
| D_ANIMATION | continuity_reviewed | **PASS** | 5 continuous-motion strips in production/REVIEW |
| E_VFX_AUDIO | required_effects_rendered | **WARN** | 2/9 events with rendered evidence |
| E_VFX_AUDIO | aftermath_checked | **WARN** | 7 events with an aftermath, 2 PASS |
| E_VFX_AUDIO | audio_visual_sync_checked | **WARN** | 9 events with sound; mix_report=True |
| E_VFX_AUDIO | set_modules_no_swallowed_code | **PASS** | lint_set_modules: 0 suspicious comment(s) in 1 file(s) |
| F_PREVIEW_REVIEW | contact_sheet_created | **PASS** | 1 sheets |
| F_PREVIEW_REVIEW | continuous_clips_inspected | **PASS** | 5 strips |
| F_PREVIEW_REVIEW | timecoded_issues_logged | **PASS** | 9 issues, 4 open |
| F_PREVIEW_REVIEW | reference_standard_compared | **WARN** | ghost_army_preview_v2_graded.mp4 (2026-11-18): FAIL ['edge_detail', 'saturation', 'saturation_seconds_over_max', 'motion_median_x1000', 'peaks_per_10s']; WARN ['hard_cuts'] |
| F_PREVIEW_REVIEW | fixes_rerendered | **PASS** | 4 fixed, 4 with after-render evidence |
| G_FINAL_DELIVERY | no_hero_placeholders | **NOT_RUN** | final phase only |
| G_FINAL_DELIVERY | grade_applied_to_all_shots | **NOT_RUN** | final phase only |
| G_FINAL_DELIVERY | native_resolution_render | **NOT_RUN** | final phase only |
| G_FINAL_DELIVERY | audio_and_subtitles_verified | **NOT_RUN** | final phase only |
| G_FINAL_DELIVERY | final_mp4_inspected | **NOT_RUN** | final phase only |
| G_FINAL_DELIVERY | lessons_saved | **NOT_RUN** | final phase only |

Totals: PASS 19, WARN 9, FAIL 0, NOT_RUN 6
