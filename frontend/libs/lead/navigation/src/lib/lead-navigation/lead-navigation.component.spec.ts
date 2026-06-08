import { ComponentFixture, TestBed } from '@angular/core/testing';
import { LeadNavigationComponent } from './lead-navigation.component';

describe('LeadNavigationComponent', () => {
  let component: LeadNavigationComponent;
  let fixture: ComponentFixture<LeadNavigationComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [LeadNavigationComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(LeadNavigationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
