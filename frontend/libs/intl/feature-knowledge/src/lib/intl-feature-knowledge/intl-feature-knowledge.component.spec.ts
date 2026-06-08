import { ComponentFixture, TestBed } from '@angular/core/testing';
import { IntlFeatureKnowledgeComponent } from './intl-feature-knowledge.component';

describe('IntlFeatureKnowledgeComponent', () => {
  let component: IntlFeatureKnowledgeComponent;
  let fixture: ComponentFixture<IntlFeatureKnowledgeComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [IntlFeatureKnowledgeComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(IntlFeatureKnowledgeComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
