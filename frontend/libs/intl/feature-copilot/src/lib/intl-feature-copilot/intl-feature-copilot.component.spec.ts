import { ComponentFixture, TestBed } from '@angular/core/testing';
import { IntlFeatureCopilotComponent } from './intl-feature-copilot.component';

describe('IntlFeatureCopilotComponent', () => {
  let component: IntlFeatureCopilotComponent;
  let fixture: ComponentFixture<IntlFeatureCopilotComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [IntlFeatureCopilotComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(IntlFeatureCopilotComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
