import { ComponentFixture, TestBed } from '@angular/core/testing';
import { LeadIntegrationComponent } from './lead-integration.component';

describe('LeadIntegrationComponent', () => {
  let component: LeadIntegrationComponent;
  let fixture: ComponentFixture<LeadIntegrationComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [LeadIntegrationComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(LeadIntegrationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
