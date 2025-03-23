from roles.domain_expert import DomainExpert #TODO: 实现各个角色类

class Session(object):
    def __init__(self, team_prompt, domain_expert_prompt, event_identifier_prompt,
                 aggregate_designer_prompt, process_modeler_prompt, model_validator_prompt,
                 business_scenario, model='gpt-4', max_round=3, validation=False):

        self.modeling_artifacts = {
            'ubiquitous_language': [],
            'events': [],
            'aggregates': [],
            'process_flows': []
        }

        # 初始化各角色处理器
        self.domain_expert = DomainExpert(
            team_prompt=team_prompt,
            role_prompt=domain_expert_prompt,
            scenario=business_scenario,
            model=model
        )

        self.event_identifier = EventIdentifier(
            team_prompt=team_prompt,
            role_prompt=event_identifier_prompt,
            model=model
        )

        self.aggregate_designer = AggregateDesigner(
            team_prompt=team_prompt,
            role_prompt=aggregate_designer_prompt,
            model=model
        )

        self.process_modeler = ProcessModeler(
            team_prompt=team_prompt,
            role_prompt=process_modeler_prompt,
            model=model
        )

        self.validator = ModelValidator(
            team_prompt=team_prompt,
            role_prompt=model_validator_prompt,
            model=model
        )

    def run_event_storming(self):
        # 领域知识提取阶段
        domain_knowledge = self.domain_expert.elicit_knowledge()
        self._update_artifacts(domain_knowledge)

        # 事件识别迭代阶段
        for _ in range(self.max_round):
            events = self.event_identifier.identify_events(
                context=self.modeling_artifacts
            )
            self._update_artifacts(events)

            # 聚合设计阶段
            aggregates = self.aggregate_designer.design_aggregates(
                current_events=events
            )
            self._update_artifacts(aggregates)

            # 流程建模阶段
            process_flows = self.process_modeler.model_process(
                events=events,
                aggregates=aggregates
            )
            self._update_artifacts(process_flows)

            # 模型验证检查点
            validation = self.validator.validate_model(
                artifacts=self.modeling_artifacts
            )
            if validation['all_passed']:
                break
            else:
                self._handle_validation_issues(validation)

        return self.modeling_artifacts, self.session_history

    def _update_artifacts(self, new_artifacts):
        # 实现模型产物的版本化合并
        if 'ubiquitous_language' in new_artifacts:
            self.modeling_artifacts['ubiquitous_language'] = merge_language(
                existing=self.modeling_artifacts['ubiquitous_language'],
                new=new_artifacts['ubiquitous_language']
            )

        # 类似处理其他产物类型（事件/聚合/流程）
        # ...

    def _handle_validation_issues(self, report):
        # 根据验证结果触发特定修正流程
        for issue in report['issues']:
            if issue['type'] == 'EVENT_MISSING_COMMAND':
                self._trigger_event_repair(issue['details'])
            elif issue['type'] == 'AGGREGATE_BOUNDARY_VIOLATION':
                self._trigger_aggregate_redesign(issue['details'])